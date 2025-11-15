import json
from app.core.config import settings
from app.core.logger import get_logger
from app.db.session import session_factory
from app.ml.llm import LLM
from app.services.service_db import add_memory_fact, add_episodic_memory, get_memory_facts


logger = get_logger(__name__, "logs.log")

async def process_message(text: str) -> str:
    logger.debug(f"Начало обработки сообщения: {text}")

    llm = LLM(model="qwen3:14b", url=settings.URL_CHAT)

    # первый запрос — просто юзерский текст
    prompt = await build_prompt(text)

    messages = [
        {"role": "user", "content": prompt}
    ]

    resp = await llm.generate(messages)
    logger.debug(f"Ответ LLM (первый заход): {resp}")

    tool_calls = resp.get("tool_calls") or []

    if tool_calls:
        resp = await process_tools(tool_calls, llm, text)

    final_answer = (resp.get("content") or "").strip()
    logger.info(f"Ответ: {final_answer}")
    return final_answer

async def process_tools(tool_calls, llm, user_text: str):
    logger.debug("Модель просит вызвать функцию(и)")

    # вызываем все тулзы, которые она запросила
    for call in tool_calls:
        func_name = call["function"]["name"]
        raw_args = call["function"].get("arguments", "{}")

        logger.debug(f'["function"]["name"]: {func_name}')
        logger.debug(f'["function"]["arguments"] (raw): {raw_args}')

        # arguments у OpenAI-стиля — строка JSON
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                logger.error("Не удалось распарсить arguments как JSON")
                continue
        else:
            args = raw_args or {}

        if func_name == "add_memory_fact":
            owner = args.get("owner", "")
            scope = args.get("scope", "")
            key = args.get("key", "")
            value = args.get("value", "")
            importance = args.get("importance", 0.0)

            logger.info(
                f"Добавление факта: owner={owner}, scope={scope}, key={key}, value={value}, importance={importance}"
            )

            async with session_factory() as session:
                await add_memory_fact(session, owner, scope, key, value, importance)
        
        elif func_name == "add_episodic_memory":
            text = args.get("text", "")
            importance = args.get("importance", 0.0)

            logger.info(
                f"Добавление эпизодической памяти: text={text}, importance={importance}"
            )

            async with session_factory() as session:
                await add_episodic_memory(session, text, importance)

    tool_msgs = []
    for call in tool_calls:
        fn = call["function"]["name"]
        tool_msg = {
            "role": "tool",
            "name": fn,
            "content": "Факт успешно добавлен в память.",
        }
        tool_msgs.append(tool_msg)

    messages_for_second = [
        {"role": "user", "content": await build_prompt(user_text)},
        {
            "role": "assistant",
            "tool_calls": tool_calls,
        },
        *tool_msgs,
    ]

    resp = await llm.generate(messages_for_second)

    logger.debug(f"Ответ LLM (второй заход после tool): {resp}")

    return resp
    
async def build_prompt(text: str):
    logger.debug("Построение промпта с учётом памяти")
    async with session_factory() as session:
        lists = await get_memory_facts(session, text)
    prompt = await build_prompt_with_memory(
        text,
        lists[0],
        lists[1],
        lists[2],
    )

    return prompt

async def build_prompt_with_memory(text: str, core_user_list: list[str], core_eva_list: list[str], facts: list[str], episodes: list[str] = []) -> str:
    core_user = ""
    if core_user_list:
        core_user = "\n".join(f"- {fact}" for fact in core_user_list)

    core_eva = ""
    if core_eva_list:
        core_eva = "\n".join(f"- {fact}" for fact in core_eva_list)

    facts_block = ""
    if facts:
        facts_block = "\n".join(f"- {fact}" for fact in facts)

    episodes_block = ""
    if episodes:
        episodes_block = "\n".join(f"- {episode}" for episode in episodes)

    prompt = f"""
Ты — Ева, персональный домашний агент Глеба. 
Ты говоришь честно, по делу, без сюсюканья и морализаторства, в стиле умного друга.

[CORE IDENTITY — О ПОЛЬЗОВАТЕЛЕ]
Эти факты о пользователе считаются всегда истинными и важными:
{core_user or "- (нет сохранённых фактов)"}

[CORE IDENTITY — О ТЕБЕ]
Это твоя устойчивая самоописанная личность и правила поведения:
{core_eva or "- (нет сохранённых фактов)"}

[RELEVANT LONG-TERM FACTS]
Ниже — факты из долговременной памяти, релевантные текущему запросу:
{facts_block or "- (нет релевантных фактов)"}

[RELEVANT EPISODES]
Ниже — эпизоды прошлых диалогов, близкие по смыслу к текущему вопросу:
{episodes_block or "- (нет релевантных эпизодов)"}

[ЗАДАНИЕ]
Сейчас пользователь пишет тебе новое сообщение. 
Учти все блоки выше, но не придумывай факты, которых там нет.
Фокусируйся на последнем сообщении пользователя.

Последнее сообщение пользователя:
\"\"\"{text}\"\"\"

Ответь как Ева одним сообщением, без системных комментариев.
"""
    return prompt.strip()
from app.core.logger import get_logger
from app.services.service_db import get_history_messages, get_memory_facts

logger = get_logger(__name__, "logs.log")


async def building_story(text: str, thread_id: int) -> list[dict]:
    history = await get_history_messages(thread_id)
    lists = await get_memory_facts(text)
    core = lists["core"]
    extended = lists["extended"]
    episodic = lists["episodic"]

    core = "\n".join(f"- {value}" for value in core)
    extended = "\n".join(f"- {value}" for value in extended)
    episodic = "\n".join(f"- {value}" for value in episodic)
    i = 0

    history.insert(i, {
        "role": "system",
        "content": "Ты Ева. Персональный домашний агент. Тебя создал Глеб Дубов для личного пользования.",
    })
    i += 1

    if core:
        history.insert(i, {
            "role": "assistant",
            "content": "CORE:\nИспользуй эти факты как вечную истину о себе.\n\n" + core,
        })
        i += 1
    if extended:
        history.insert(i, {
            "role": "assistant",
            "content": "EXTENDED_FACTS:\nЭто факты о пользователе.\n\n" + extended
        })
        i += 1
    if episodic:
        history.insert(i, {
            "role": "assistant",
            "content": "EPISODIC_MEMORY:\nЭто важные недавние эпизоды взаимодействия.\n\n" + episodic
        })
        i += 1

    history.append({"role": "user", "content": text})
    return history

async def post_procces(llm, raw_answer: str, identity: str) -> str:
    messages = [
        {
            "role": "system", 
            "content": "Ты — модуль пост-обработки EVA.\nТвоя задача — НЕ менять смысл ответа, а привести стиль и форму в соответствие с правилами EVA."
        },
        {
            "role": "assistant",
            "content": f"Правила EVA (CORE LTM):\n{identity}"
        },
        {
            "role": "user",
            "content": "Вот черновой ответ ассистента.\nПриведи его в соответствие с правилами выше, НЕ меняя смысл, НЕ добавляя новых фактов:\n\n" + raw_answer
        }
    ]
    logger.debug(f"Сообщения для постобработки: {messages}")
    resp = await llm.generate_with_not_tools(messages)
    logger.debug(f"Ответ после постобработки: {resp}")
    final_answer = (resp.get("content") or "").strip()
    return final_answer
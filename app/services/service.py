from datetime import datetime
import json
from app.core.config import settings
from app.core.logger import get_logger
from app.db.session import session_factory
from app.ml.llm import LLM
from app.services.service_db import add_episodic_memory, add_memory_fact, add_message, get_last_id_conversation, get_memory_core_facts
from app.services.service_llm import building_story, post_procces


logger = get_logger(__name__, "logs.log")
llm = LLM(model=settings.LLM_MODEL, url=settings.URL_CHAT)

async def process_message(text: str, user_id: int) -> str:
    logger.debug(f"Начало обработки сообщения")

    last_id = await get_last_id_conversation(user_id)

    messages = await building_story(last_id, text, user_id)
    logger.debug(f"История сообщений для LLM: {messages}")
    resp = await llm.generate(messages)
    logger.debug(f"Ответ LLM: {resp}")

    resp = await process_tools(resp, user_id, messages)
    final_answer = (resp.get("content") or "").strip()

    core_eva = await get_memory_core_facts()
    core_eva = "\n".join(f"- {value}" for value in core_eva)
    final_answer = await post_procces(llm, final_answer, core_eva)

    await add_message(last_id, "user", text)
    await add_message(last_id, "assistant", final_answer)

    logger.info(f"Ответ EVA: {final_answer}")
    return final_answer


async def process_tools(resp, user_id: int, history: list[dict]):
    tool_calls = resp.get("tool_calls") or []
    if tool_calls:
        history.append({"role": "assistant","tool_calls": tool_calls})
    while tool_calls:
        logger.debug(f"Кол-во запрошенных функций: {len(tool_calls)}")
        for call in tool_calls:
            func_name = call["function"]["name"]
            raw_args = call["function"].get("arguments", "{}")

            logger.debug(f'["function"]["name"]: {func_name}')
            logger.debug(f'["function"]["arguments"] (raw): {raw_args}')

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
                owner_id = user_id if owner != "Eva" else 0
                scope = args.get("scope", "")
                value = args.get("value", "")
                importance = args.get("importance", 0.0)

                logger.info(
                    f"Добавление факта: owner={owner}, scope={scope}, value={value}, importance={importance}"
                )

                await add_memory_fact(owner, owner_id, scope, value, importance)
                tool_answer = "Факт успешно добавлен."
                
            elif func_name == "day_info":
                now = datetime.now()
                tool_answer = f"Время: {now.strftime('%H:%M')}\nДата: {now.strftime('%Y-%m-%d')}\nДень недели: {now.strftime('%A')}"

            elif func_name == "add_episodic_memory":
                text = args.get("text", "")
                importance = args.get("importance", 0.5)
                await add_episodic_memory(user_id, text, 0.5)
                tool_answer = "Эпизод успешно сохранён в память."
            
            history.append({"role": "tool", "name": func_name, "content": tool_answer})

        logger.debug(f"История после tool: {history}")
        resp = await llm.generate(history)
        logger.debug(f"Ответ LLM (tool): {resp}")

        tool_calls = resp.get("tool_calls") or []
    
    logger.debug(f"История после завершения всех tool вызовов: {history}")
    return resp
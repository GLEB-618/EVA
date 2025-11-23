from app.core.logger import get_logger
from app.services.service_db import get_episodic_memory, get_history_messages, get_memory_core_facts, get_memory_facts

logger = get_logger(__name__, "logs.log")


async def building_story(last_id: int, text: str, user_id: int) -> list[dict]:
    history = await get_history_messages(last_id)
    lists = await get_memory_facts(text, user_id)
    eva_list = await get_memory_core_facts()
    episodic_list = await get_episodic_memory(user_id, text)
    core_eva_list = "\n".join(f"- {value}" for value in eva_list)
    core_user_list = "\n".join(f"- {value}" for value in lists[0])
    extended_list = "\n".join(f"- {value}" for value in lists[1])
    episodic_list = "\n".join(f"- {value}" for value in episodic_list)

    i = 0

    if core_eva_list:
        history.insert(i, {
            "role": "system",
            "content": "Ты — Eva, персональный домашний агент Глеба. Вот твои основные установки (CORE_EVA_FACTS):\n" + core_eva_list,
        })
        i += 1
    if core_user_list:
        history.insert(i, {
            "role": "assistant",
            "content": "CORE_USER_FACTS:\nИспользуй эти факты как вечную истину о пользователе. Не цитируй список вслух, просто опирайся на него.\n\n" + core_user_list,
        })
        i += 1
    if extended_list:
        history.insert(i, {
            "role": "assistant",
            "content": "EXTENDED_USER_FACTS:\nЭто расширенные факты о пользователе. Используй их в ответах по смыслу, но не читай вслух.\n\n" + extended_list
        })
        i += 1
    if episodic_list:
        history.insert(i, {
            "role": "assistant",
            "content": "EPISODIC_MEMORY:\nЭто важные недавние эпизоды взаимодействия. Опирайся на них по смыслу, но не цитируй список вслух.\n\n" + episodic_list
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
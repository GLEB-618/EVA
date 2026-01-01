import json
from app.core.config import settings
from app.core.logger import get_logger
from app.ml.llm import LLM
from app.services.tools.online_search import search_web
from app.services.service_db import add_message
from app.services.service_llm import building_story
from app.services.tools.spotify import get_top_tracks


logger = get_logger(__name__, "logs.log")
llm = LLM(model=settings.LLM_MODEL, url=settings.URL_CHAT)


async def process_message(text: str, thread_id: int) -> str:
    logger.debug(f"Начало обработки сообщения")

    messages = await building_story(text, thread_id)
    logger.debug(f"История сообщений для LLM: {messages}")
    resp = await llm.generate(messages)
    logger.debug(f"Ответ LLM: {resp}")

    await add_message(thread_id, "user", text)

    resp = await process_tools(resp, messages, thread_id)
    final_answer = (resp.get("content") or "").strip()

    # final_answer = await post_procces(llm, final_answer, core_eva)

    await add_message(thread_id, "assistant", final_answer)

    logger.info(f"Ответ EVA: {final_answer}")
    return final_answer


async def process_tools(resp, history: list[dict], thread_id: int) -> dict:
    tool_calls = resp.get("tool_calls") or []
    if tool_calls:
        history.append({"role": "assistant","tool_calls": tool_calls})
        await add_message(thread_id, "assistant", str(tool_calls))
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

            # if func_name == "add_memory_fact":
            #     owner_id = user_id
            #     scope = args.get("scope", "")
            #     value = args.get("value", "")
            #     importance = args.get("importance", 0.0)

            #     logger.info(
            #         f"Добавление факта: scope={scope}, value={value}, importance={importance}"
            #     )

            #     await add_memory_fact(owner_id, scope, value, importance)
            #     tool_answer = "Факт успешно добавлен."

            # elif func_name == "add_episodic_memory":
            #     text = args.get("text", "")
            #     importance = args.get("importance", 0.5)

            #     logger.info(
            #         f"Добавление эпизода: text={text}, importance={importance}"
            #     )

            #     await add_episodic_memory(user_id, text, 0.5)
            #     tool_answer = "Эпизод успешно сохранён в память."

            if func_name == "search_web":
                query = args.get("query", "")
                n_results = args.get("n_results", 5)
                region = args.get("region", "ru-ru")
                safesearch = args.get("safesearch", "moderate")
                with_content = args.get("with_content", True)

                logger.info(
                    f"Выполнение веб-поиска: query={query}, n_results={n_results}, region={region}, safesearch={safesearch}, with_content={with_content}"
                )

                search_results = await search_web(query, n_results, region)
                logger.debug(f"Результаты поиска: {search_results}")
                tool_answer = f"Результаты поиска: {search_results}"

            elif func_name == "top_tracks":
                limit = args.get("limit", 10)
                offset = args.get("offset", 0)
                time_range = args.get("time_range", "medium_term")

                logger.info(
                    f"Получение топ-треков: limit={limit}, offset={offset}, time_range={time_range}"
                )

                tracks = await get_top_tracks(limit=limit, offset=offset, time_range=time_range)
                logger.debug(f"Топ треки: {tracks}")
                tool_answer = f"Ваши топ треки:\n{tracks}"
            
            history.append({"role": "tool", "name": func_name, "content": tool_answer})
            await add_message(thread_id, "tool", tool_answer, func_name)

        resp = await llm.generate(history)
        logger.debug(f"Ответ LLM (tool): {resp}")

        tool_calls = resp.get("tool_calls") or []
    
    logger.debug(f"История после завершения всех tool вызовов: {history}")
    return resp
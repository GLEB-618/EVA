from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.ml.embedding import EmbeddingModel
from app.repository.repo import insert_fact, insert_episod, select_facts

from app.core.logger import get_logger

logger = get_logger(__name__, "logs.log")

async def add_memory_fact(session: AsyncSession, owner: str, owner_id: int, scope: str, value: str, importance: float):
    await insert_fact(session, owner, owner_id, scope, value, importance)
    await session.commit()

async def add_episodic_memory(session: AsyncSession, text: str, importance: float):
    emb = EmbeddingModel(settings.EMBEDDING_MODEL)
    vector = (await emb.encode([text]))[0]
    await insert_episod(session, text, vector, importance)
    await session.commit()

async def get_memory_facts(session: AsyncSession, text: str, user_id: int) -> list[list[str]]:
    logger.debug("Получение фактов из базы данных")
    lists = await select_facts(session, user_id)
    emb = EmbeddingModel(settings.EMBEDDING_MODEL)

    logger.debug(f"Количество фактов в user core памяти: {len(lists[0])}")
    logger.debug(f"Количество фактов в eva core памяти: {len(lists[1])}")
    logger.debug(f"Количество фактов в extended памяти: {len(lists[2])}")

    if not lists[2]:
        value = []
    else:
        value = await emb.get_similarities(text, lists[2])

    return [lists[0], lists[1], value]

# async def add_user(session: AsyncSession, tg_id: int, nickname: str):
#     await insert_user(session, tg_id, nickname)
#     await session.commit()

# async def check_user(session: AsyncSession, tg_id: int, nickname: str):
#     name = await check_user_by_id(session, tg_id)
#     if not name:
#         logger.debug(f"Пользователь с tg_id={tg_id} не найден в БД. Добавляем...")
#         await add_user(session, tg_id, nickname)
#         name = f"Неизвестный пользователь ({nickname})"
#     return name

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.ml.embedding import EmbeddingModel
from app.repository.repo import insert_fact, insert_episod, select_facts

from app.core.logger import get_logger

logger = get_logger(__name__, "logs.log")

async def add_memory_fact(session: AsyncSession, owner: str, scope: str, key: str, value: str, importance: float):
    await insert_fact(session, owner, scope, key, value, importance)
    await session.commit()

async def add_episodic_memory(session: AsyncSession, text: str, importance: float):
    emb = EmbeddingModel(settings.EMBEDDING_MODEL)
    vector = (await emb.encode([text]))[0]
    await insert_episod(session, text, vector, importance)
    await session.commit()

async def get_memory_facts(session: AsyncSession, text: str):
    logger.debug("Получение фактов из базы данных")
    lists = await select_facts(session)
    emb = EmbeddingModel(settings.EMBEDDING_MODEL)

    logger.debug(f"Количество фактов в user core памяти: {len(lists[0])}")
    logger.debug(f"Количество фактов в eva core памяти: {len(lists[1])}")
    logger.debug(f"Количество фактов в extended памяти: {len(lists[2])}")

    if not lists[2]:
        value = []
    else:
        value = await emb.get_similarities(text, lists[2])

    return [lists[0], lists[1], value]



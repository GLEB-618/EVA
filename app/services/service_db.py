from typing import Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings
from app.db.session import session_factory
from app.ml.embedding import EmbeddingModel
from app.repository.repo import insert_conversation, insert_fact, insert_episod, insert_messages, select_core_facts, select_facts, select_last_id_conversation, select_messages_by_conversation, select_relevant_episodic_memory

from app.core.logger import get_logger

logger = get_logger(__name__, "logs.log")
emb = EmbeddingModel(settings.EMBEDDING_MODEL)
alpha = 0.7
beta = 0.3
MEMORY_TOP_K = 5


def _normalize(arr: np.ndarray) -> np.ndarray:
    """Приводим массив к [0, 1], аккуратно обрабатываем константный случай."""
    if arr.size == 0:
        return arr
    arr_min = float(arr.min())
    arr_max = float(arr.max())
    if arr_max - arr_min < 1e-8:
        # все одинаковые — пусть будет середина
        return np.full_like(arr, 0.5, dtype=float)
    return (arr - arr_min) / (arr_max - arr_min)

async def _hybrid_method(text: str, lists: list[tuple[Any, float]]) -> list[str]:
    texts = [value for value, _imp in lists]
    importances = np.array([imp for _value, imp in lists], dtype=float)

    query_emb = await emb.encode([text])
    corpus_emb = await emb.encode(texts)

    sims = cosine_similarity(query_emb, corpus_emb)[0]

    sims_norm = _normalize(sims)
    imps_norm = _normalize(importances)

    scores = alpha * sims_norm + beta * imps_norm

    top_indices = scores.argsort()[::-1][:MEMORY_TOP_K]
    top_texts = [texts[i] for i in top_indices]
    logger.debug("Топ факты (value, score): "+ repr([(texts[i], float(scores[i])) for i in top_indices]))

    return top_texts


# MEMORY_FACTS
async def add_memory_fact(owner: str, owner_id: int, scope: str, value: str, importance: float):
    async with session_factory() as session:
        await insert_fact(session, owner, owner_id, scope, value, importance)
        await session.commit()

async def get_memory_facts(text: str, user_id: int) -> list[list[str]]:
    logger.debug("Получение фактов из базы данных")
    async with session_factory() as session:
        lists = await select_facts(session, user_id)
        core_facts = lists[0]
        extended_facts = lists[1]

    logger.debug(f"Количество фактов в user core памяти: {len(lists[0])}")
    logger.debug(f"Количество фактов в extended памяти: {len(lists[1])}")

    if not extended_facts:
        return [core_facts, []]
    
    top_extended = await _hybrid_method(text, extended_facts)

    # Возвращаем в том же формате, что и раньше: [core, extended]
    return [core_facts, top_extended]

async def get_memory_core_facts() -> list[str]:
    async with session_factory() as session:
        ls = await select_core_facts(session)
    logger.debug(f"Количество фактов в core памяти EVA: {len(ls)}")
    return ls

# EPISODIC_MEMORY
async def add_episodic_memory(owner_id: int, text: str, importance: float):
    async with session_factory() as session:
        vector = await emb.encode_one(text)
        await insert_episod(session, owner_id, text, vector, importance)
        await session.commit()

async def get_episodic_memory(owner_id: int, text: str) -> list[str]:
    async with session_factory() as session:
        episodic_facts = await select_relevant_episodic_memory(session, owner_id)

    if not episodic_facts:
        return []
    
    top_episodic = await _hybrid_method(text, episodic_facts)

    return top_episodic

async def get_history_messages(conversation_id: int) -> list[dict[str, str]]:
    async with session_factory() as session:
        result = await select_messages_by_conversation(session, conversation_id)
    return result

async def add_message(conversation_id: int, role: str, content: str):
    logger.debug(f"Добавление сообщения в базу данных: conversation_id={conversation_id}, role={role}, content={content[:30]}...")
    async with session_factory() as session:
        await insert_messages(session, conversation_id, role, content)
        await session.commit()

async def add_conversation(user_id: int) -> int:
    async with session_factory() as session:
        con_id = await insert_conversation(session, user_id)
        await session.commit()
    return con_id

async def get_last_id_conversation(user_id: int) -> int:
    async with session_factory() as session:
        last_id = await select_last_id_conversation(session, user_id)
    if last_id is None:
        last_id = await add_conversation(user_id)
    logger.debug(f"Последний ID разговора для пользователя {user_id}: {last_id}")
    return last_id
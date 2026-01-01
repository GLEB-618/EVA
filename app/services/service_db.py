from typing import Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.core.config import settings
from app.db.session import session_factory
from app.ml.embedding import EmbeddingModel
from app.repository.repo import insert_fact, insert_messages, select_messages_by_thread, select_memory

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

async def _hybrid_method(text: str, lists: list[dict[str, Any]]) -> list[str]:
    texts = [item["value"] for item in lists]
    importances = np.array([item["importance"] for item in lists], dtype=float)

    print(texts, importances)

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
async def add_memory_fact(scope: str, value: str, importance: float):
    async with session_factory() as session:
        await insert_fact(session, scope, value, importance)
        await session.commit()

async def get_memory_facts(text: str) -> dict[str, Any]:
    async with session_factory() as session:
        lists = await select_memory(session)
    extended_facts = lists["extended"]
    logger.debug(f"Количество фактов в core памяти: {len(lists['core'])}")
    logger.debug(f"Количество фактов в extended памяти: {len(extended_facts)}")
    logger.debug(f"Количество фактов в episodic памяти: {len(lists['episodic'])}")

    top_extended = await _hybrid_method(text, extended_facts)
    lists["extended"] = top_extended

    return lists

async def add_message(thread_id: int, role: str, content: str, name: str|None = None):
    logger.debug(f"Добавление сообщения в базу данных: thread_id={thread_id}, role={role}, content={content[:30]}...")
    async with session_factory() as session:
        await insert_messages(session, thread_id, role, content, name)
        await session.commit()

async def get_history_messages(thread_id: int) -> list[dict[str, str]]:
    async with session_factory() as session:
        result = await select_messages_by_thread(session, thread_id)
    return result
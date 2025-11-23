import asyncio
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.logger import get_logger

logger = get_logger(__name__, "logs.log")


class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._executor = ThreadPoolExecutor()
        logger.info(f"Загружаю embedding-модель: {model_name}")
        self._model = SentenceTransformer(model_name)
        logger.info(f"Embedding-модель {model_name} успешно загружена")

    async def encode(self, inputs: list[str]):
        loop = asyncio.get_running_loop()
        func = partial(self._model.encode, inputs)

        return await loop.run_in_executor(self._executor, func)
    
    async def encode_one(self, text: str) -> list[float]:
        emb = await self.encode([text])  # shape = (1, dim)
        return emb[0].tolist()
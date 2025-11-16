import asyncio
from functools import partial
from concurrent.futures import ThreadPoolExecutor
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
    
    async def get_similarities(self, text: str, corpus: list[str], top_k: int = 3):
        user_embedding = await self.encode([text])
        corpus_embeddings = await self.encode(corpus)

        sims = cosine_similarity(user_embedding, corpus_embeddings)[0]

        top_indices = sims.argsort()[::-1][:top_k] # Индексы самых близких вопросов. В порядке убывания
        logger.debug(f"top_values: {[sims[i] for i in top_indices]}")
        top_values = [corpus[i] for i in top_indices]
        return top_values
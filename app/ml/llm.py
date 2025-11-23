from ollama import AsyncClient
from app.core.config import TOOLS
from app.core.logger import get_logger

logger = get_logger(__name__, "logs.log")

class LLM:
    def __init__(self, model: str, url: str = "http://localhost:11434"):
        self.model = model
        self.client = AsyncClient(host=url)
        logger.debug(f"Инициализирован LLM с моделью {model} и URL {url}")

    async def generate(self, messages: list[dict]):
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            think=True,
            tools=TOOLS
        )
        return response["message"]
    
    async def generate_with_not_tools(self, messages: list[dict]):
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            think=True,
        )
        return response["message"]
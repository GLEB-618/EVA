from ollama import AsyncClient
from app.core.logger import get_logger
from app.core.tools import MAIN_TOOL

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
            tools=MAIN_TOOL,
        )
        return response["message"]
    
    async def generate_with_temp(self, messages: list[dict], temp: float):
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            options = {
                "temperature": temp, 
            },
        )
        return response["message"]
    
    async def generate_with_not_tools(self, messages: list[dict]):
        response = await self.client.chat(
            model=self.model,
            messages=messages,
            think=True,
        )
        return response["message"]
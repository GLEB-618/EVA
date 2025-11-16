from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    BOT_TOKEN: str
    TELEGRAM_API_BASE_URL: str
    EMBEDDING_MODEL: str
    LLM_MODEL: str
    URL_CHAT: str
    LOG_LEVEL: str
    
    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_memory_fact",
            "description": (
                "Добавляет один факт в таблицу memory_facts. "
                "Вызывай, когда из диалога появляется устойчивый факт о пользователе или о Eva (о тебе)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": (
                            "Кого касается факт. Например, 'Глеб' для конкретного пользователя "
                            "или 'Eva' для фактов о самой Eva (о тебе)."
                        )
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["core", "extended"],
                        "description": (
                            "'core' — ядро личности, постоянные правила.\n"
                            "'extended' — факты про проекты, интересы, прошлые разговоры."
                        )
                    },
                    "value": {
                        "type": "string",
                        "description": "Текстовое описание факта."
                    },
                    "importance": {
                        "type": "number",
                        "description": (
                            "Важность факта от 0.0 до 1.0. Чем больше, тем важнее факт для будущих диалогов."
                        ),
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["owner", "value"]
            }
        }
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "add_episodic_memory",
    #         "description": (
    #             "Сохраняет эпизод из диалога в таблицу episodic_memory. "
    #             "Используй, когда произошёл важный фрагмент разговора "
    #             "(обсуждали проект, сделали вывод, произошла заметная сцена)."
    #         ),
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "text": {
    #                     "type": "string",
    #                     "description": (
    #                         "Краткое текстовое описание эпизода. "
    #                         "Например: 'обсуждали выбор между qwen2.5 и qwen3 для агента Евы'."
    #                     )
    #                 },
    #                 "importance": {
    #                     "type": "number",
    #                     "description": (
    #                         "Важность эпизода от 0.0 до 1.0. "
    #                         "Чем выше, тем больше вероятность, что его будут вытаскивать позже."
    #                     ),
    #                     "minimum": 0.0,
    #                     "maximum": 1.0
    #                 }
    #             },
    #             "required": ["text"]
    #         }
    #     }
    # },
]
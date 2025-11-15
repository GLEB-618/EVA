import asyncio
from app.bot.bot import run_bot
from app.core.logger import get_logger


if __name__ == "__main__":
    get_logger("aiogram", "aiogram.log")
    asyncio.run(run_bot())
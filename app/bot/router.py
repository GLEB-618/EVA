from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReactionTypeEmoji, FSInputFile
from aiogram.enums.chat_type import ChatType
from app.core.logger import get_logger
from app.services.service import process_message


router = Router()
logger = get_logger(__name__, "logs.log")


@router.message()
async def handler(msg: Message):
    if msg.text is None:
        return
    text = msg.text.strip()
    if msg.message_thread_id is None:
        await msg.reply("Пожалуйста, используйте темы для общения с ботом в группах.")
        return
    thread_id = msg.message_thread_id

    logger.info(f"Получено сообщение в теме {thread_id}: {text}")

    answer = await process_message(text, thread_id)
    await msg.reply(text=answer)
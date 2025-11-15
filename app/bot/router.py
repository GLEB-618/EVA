from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReactionTypeEmoji, FSInputFile
from aiogram.enums.chat_type import ChatType
from app.core.logger import get_logger
from app.services.service import process_message


router = Router()
logger = get_logger(__name__, "logs.log")


@router.message(F.text, F.chat.type == ChatType.PRIVATE)
async def talk(msg: Message):
    text = msg.text.strip()
    answer = await process_message(text)
    await msg.reply(text=answer)
    
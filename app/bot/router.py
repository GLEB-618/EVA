from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReactionTypeEmoji, FSInputFile
from aiogram.enums.chat_type import ChatType
from app.core.logger import get_logger
# from app.db.session import session_factory
# from app.services.service_db import check_user
from app.services.service import process_message
from app.services.service_db import add_conversation


router = Router()
logger = get_logger(__name__, "logs.log")


@router.message(Command('chat'), F.text, F.chat.type == ChatType.PRIVATE)
async def chat(msg: Message):
    logger.info(f"Создание нового чата для пользователя {msg.from_user.id}")
    await add_conversation(msg.from_user.id)
    await msg.reply(text="Создан новый чат для хранения истории сообщений.")

@router.message(F.text, F.chat.type == ChatType.PRIVATE)
async def talk(msg: Message):
    text = msg.text.strip()
    user_id = msg.from_user.id
    user_name = msg.from_user.first_name
    logger.info(f"Новое сообщение от {user_name} ({user_id}): {text}")
    # async with session_factory() as session:
    #     name = await check_user(session, user_id, user_name)
    answer = await process_message(text, user_id)
    await msg.reply(text=answer)
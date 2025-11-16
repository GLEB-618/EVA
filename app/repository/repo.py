from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Row, Sequence, delete, exists, select, or_, and_

from app.models.model import *

async def insert_fact(session: AsyncSession, owner: str, owner_id: int, scope: str, value: str, importance: float) -> None:
    new = MemoryFacts(owner=owner, owner_id=owner_id, scope=scope, value=value, importance=importance)
    session.add(new)
    await session.flush()

async def insert_episod(session: AsyncSession, text: str, embedding: bytes, importance: float) -> None:
    new = EpisodicMemory(text=text, embedding=embedding, importance=importance)
    session.add(new)
    await session.flush()

async def select_facts(session: AsyncSession, user_id: int) -> list[list[str]]:
    stmt = select(MemoryFacts.owner_id, MemoryFacts.value, MemoryFacts.scope).order_by(MemoryFacts.importance.desc())
    result = await session.execute(stmt)
    rows = result.all()  # [(owner_id, value, scope), ...]

    user_core_values = [value for owner_id, value, scope in rows if owner_id == user_id and scope == "core"]
    eva_core_values = [value for owner_id, value, scope in rows if owner_id == 0 and scope == "core"]
    extended_values = [value for owner_id, value, scope in rows if owner_id == user_id and scope == "extended"]

    result_lists = [user_core_values, eva_core_values, extended_values]  # [{us}, {ev}, {ex}] 
    return result_lists

# async def insert_user(session: AsyncSession, tg_id: int, nickname: str) -> None:
#     new = Users(tg_id=tg_id, nickname=nickname)
#     session.add(new)
#     await session.flush()

# async def check_user_by_id(session: AsyncSession, tg_id: int) -> str|bool:
#     stmt = select(Users.real_name, Users.nickname).where(Users.tg_id == tg_id).limit(1)

#     result = await session.execute(stmt)
#     row = result.first()  # вернёт (real_name, nickname) или None

#     if row is None:
#         return False

#     real_name, nickname = row
#     return real_name or f"Неизвестный пользователь ({nickname})"
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Row, Sequence, delete, select, or_, and_

from app.models.model import *

async def insert_fact(session: AsyncSession, owner: str, scope: str, key: str, value: str, importance: float):
    new = MemoryFacts(owner=owner, scope=scope, key=key, value=value, importance=importance)
    session.add(new)
    await session.flush()

async def insert_episod(session: AsyncSession, text: str, embedding: bytes, importance: float):
    new = EpisodicMemory(text=text, embedding=embedding, importance=importance)
    session.add(new)
    await session.flush()

async def select_facts(session: AsyncSession):
    stmt = select(MemoryFacts.owner, MemoryFacts.value, MemoryFacts.scope).order_by(MemoryFacts.scope)
    result = await session.execute(stmt)
    rows = result.all()  # [(owner, value, scope), ...]

    user_core_values = [value for owner, value, scope in rows if owner != "Eva" and scope == "core"]
    eva_core_values = [value for owner, value, scope in rows if owner == "Eva" and scope == "core"]
    extended_values = [value for owner, value, scope in rows if scope == "extended"]

    result_lists = [user_core_values, eva_core_values, extended_values]
    return result_lists
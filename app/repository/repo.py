from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Row, Sequence, delete, exists, select, or_, and_

from app.models.model import *

alpha = 0.7
beta = 0.3

async def insert_fact(session: AsyncSession, owner: str, owner_id: int, scope: str, value: str, importance: float) -> None:
    new = MemoryFacts(owner=owner, owner_id=owner_id, scope=scope, value=value, importance=importance)
    session.add(new)
    await session.flush()

async def insert_episod(session: AsyncSession, owner_id: int, text: str, embedding: list[float], importance: float) -> None:
    new = EpisodicMemory(owner_id=owner_id, text=text, embedding=embedding, importance=importance)
    session.add(new)
    await session.flush()

async def select_facts(session: AsyncSession, user_id: int):
    stmt = (
        select(
            MemoryFacts.value,
            MemoryFacts.scope,
            MemoryFacts.importance,
        )
        .where(MemoryFacts.owner_id == user_id)
        .order_by(MemoryFacts.importance.desc())
    )

    result = await session.execute(stmt)
    rows = result.all()  # [(value, scope, importance), ...]

    core_facts: list[str] = []
    extended_facts: list[tuple[str, float]] = []

    for value, scope, importance in rows:
        if scope == "core":
            core_facts.append(value)
        elif scope == "extended":
            extended_facts.append((value, float(importance)))

    return [core_facts, extended_facts]

async def select_core_facts(session: AsyncSession) -> list[str]:
    stmt = (
        select(MemoryFacts.value)
        .where(
            MemoryFacts.owner_id == 0,
            MemoryFacts.scope == "core",
        )
        .order_by(MemoryFacts.importance.desc())
    )

    result = await session.scalars(stmt)
    return list(result)

async def select_relevant_episodic_memory(session: AsyncSession, owner_id: int, limit: int = 5):
    stmt = (
        select(
            EpisodicMemory.text,
            EpisodicMemory.importance
        )
        .where(EpisodicMemory.owner_id == owner_id)
        .order_by(EpisodicMemory.importance.desc())
        .limit(limit)
    )

    result = await session.execute(stmt)
    rows = result.all()
    return [(value, float(importance)) for value, importance in rows]

async def insert_messages(session: AsyncSession, conversation_id: int, role: str, content: str) -> None:
    new = Messages(conversation_id=conversation_id, role=role, content=content)
    session.add(new)
    await session.flush()

async def select_messages_by_conversation(session: AsyncSession, conversation_id: int, limit: int = 20) -> list[dict[str, Any]]:
    stmt = select(Messages.role, Messages.content).where(Messages.conversation_id == conversation_id).order_by(Messages.id.desc())
    result = await session.execute(stmt)
    rows = result.all()  # [(role, content), ...]

    result = await session.execute(stmt)
    rows = list(result.all())
    rows = list(reversed(rows))

    result_lists = [{"role": role, "content": content} for role, content in rows]
    return result_lists

async def insert_conversation(session: AsyncSession, user_id: int) -> int:
    new = Conversations(user_id=user_id)
    session.add(new)
    await session.flush()
    return new.id

async def select_last_id_conversation(session: AsyncSession, user_id: int) -> int | None:
    stmt = select(func.max(Conversations.id)).where(Conversations.user_id == user_id)
    result = await session.execute(stmt)
    (last_id,) = result.one()  # last_id может быть None, если таблица пустая
    return last_id
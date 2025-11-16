from datetime import datetime
from typing import Annotated
from sqlalchemy import ARRAY, BigInteger, DateTime, Float, LargeBinary, Text, Boolean, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
stx = Annotated[str, mapped_column(Text)]

# class Users(Base):
#     __tablename__ = "users"

#     id: Mapped[intpk]
#     tg_id: Mapped[int] = mapped_column(BigInteger)
#     nickname: Mapped[stx]
#     real_name: Mapped[stx] = mapped_column(nullable=True, default=None)
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#     )

class MemoryFacts(Base):
    __tablename__ = "memory_facts"

    id: Mapped[intpk]
    owner: Mapped[stx]
    owner_id: Mapped[int] = mapped_column(BigInteger)
    scope: Mapped[stx]
    value: Mapped[stx]
    importance: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class EpisodicMemory(Base):
    __tablename__ = "episodic_memory"

    id: Mapped[intpk]
    text: Mapped[stx]
    embedding: Mapped[list[float]] = mapped_column(ARRAY(Float))
    importance: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
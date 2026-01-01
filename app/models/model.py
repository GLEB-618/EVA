from datetime import datetime
from typing import Annotated
from sqlalchemy import ARRAY, BigInteger, DateTime, Float, ForeignKey, LargeBinary, Text, Boolean, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

intpk = Annotated[int, mapped_column(primary_key=True)]
stx = Annotated[str, mapped_column(Text)]


class Memory(Base):
    __tablename__ = "memory"

    id: Mapped[intpk]
    scope: Mapped[stx]
    value: Mapped[stx]
    importance: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[intpk]
    thread_id: Mapped[int] = mapped_column(
        BigInteger,
    )
    role: Mapped[stx]
    name: Mapped[stx] = mapped_column(
        nullable=True
    )
    content: Mapped[stx]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class Applications(Base):
    __tablename__ = "applications"

    id: Mapped[intpk]
    name: Mapped[stx]
    path: Mapped[stx]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = 'notes'

    note_id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    content: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

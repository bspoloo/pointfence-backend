

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String
from app.db.database import Base
from typing import List


class Player(Base):
    __tablename__ = "players"

    player_name: Mapped[str] = mapped_column(String(length=50), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    user: Mapped["User | None"] = relationship(back_populates="player")

    savings_status: Mapped[List["SavingStatus"]] = relationship(back_populates="player")

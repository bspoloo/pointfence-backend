
from app.db.database import Base
from sqlalchemy import ForeignKey, Integer, String, Boolean
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

class SavingStatus(Base):
    __tablename__ = "savings_status"

    user_position: Mapped[str] = mapped_column(String(length=50), nullable=False)

    unlock: Mapped[bool] = mapped_column(Boolean, default=False)
    life: Mapped[int] = mapped_column(Integer, nullable=False)

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    
    level: Mapped["Level"] = relationship(back_populates="savings_status")
    player: Mapped["Player"] = relationship(back_populates="savings_status")
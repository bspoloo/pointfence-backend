
from app.db.database import Base
from sqlalchemy import String
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Level(Base):
    __tablename__ = "levels"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    spawn_position: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    savings_status: Mapped[List["SavingStatus"]] = relationship(back_populates="level")
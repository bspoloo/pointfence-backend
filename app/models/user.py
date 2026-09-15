
from app.db.database import Base
from sqlalchemy import String
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    names: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password: Mapped[str]  = mapped_column(String(150), nullable=False)

    images: Mapped[List["Image"]] = relationship(back_populates="user")
    masks: Mapped[List["Mask"]] = relationship(back_populates="user")
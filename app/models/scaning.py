

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Scanning(Base):
    __tablename__ = "scannings"
    
    filename: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(100), nullable=False)

    object_id: Mapped[int] = mapped_column(ForeignKey("objects.id"), unique=True, nullable=False)

    object: Mapped["Object | None"] = relationship(back_populates="scanning", uselist=False)

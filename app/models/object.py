from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Object(Base):
    __tablename__ = "objects"
    
    filename: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(100), nullable=False)

    image_mask_id: Mapped[int] = mapped_column(ForeignKey("image_masks.id"), unique=True, nullable=False)

    image_mask: Mapped["ImageMask | None"] = relationship(back_populates="object", uselist=False)
    scanning: Mapped["Scanning | None"] = relationship(back_populates="object",uselist=False)
    
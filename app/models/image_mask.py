

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ImageMask(Base):
    __tablename__ = "image_masks"
    
    filename: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(100), nullable=False)

    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), unique=True, nullable=False)
    mask_id: Mapped[int] = mapped_column(ForeignKey("masks.id"), unique=True, nullable=False)

    image: Mapped["Image"] = relationship(back_populates="image_mask")
    mask: Mapped["Mask"] = relationship(back_populates="image_mask")

    object: Mapped["Object | None"] = relationship(back_populates="image_mask")


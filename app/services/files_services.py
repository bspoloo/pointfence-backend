
from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.image import Image
from app.models.image_mask import ImageMask
from app.models.mask import Mask
from app.models.object import Object
from app.models.scaning import Scanning
from app.models.user import User
from app.schemas.create_file import CreateModel, CreateObject, CreateFile


from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.image import Image
from app.models.mask import Mask
from app.schemas.create_file import CreateFile


async def get_image_and_mask_by_filename(filename: str,db: Session) -> tuple[Image, Mask]:
    try:
        image = db.scalar(
            select(Image)
            .where(Image.filename == filename)
            .where(Image.deleted_at.is_(None))
        )

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la imagen: {filename}"
            )

        mask = db.scalar(
            select(Mask)
            .where(Mask.filename == filename)
            .where(Mask.deleted_at.is_(None))
        )

        if not mask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la máscara asociada a: {filename}"
            )

        return image, mask

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener imagen y máscara: {str(e)}"
        )

async def get_scanning_by_filename(filename: str,db: Session) -> Scanning:
    try:
        scanning = db.scalar(
            select(Scanning)
            .where(Scanning.filename == filename)
            .where(Scanning.deleted_at.is_(None))
        )

        if not scanning:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la escaneo ena la base de datos: {filename}"
            )

        return scanning

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener escaneo: {str(e)}"
        )


async def save_image(file: CreateFile, db: Session) -> Image:
    try:
        existing_image = db.scalar(
            select(Image)
            .where(Image.filename == file.filename)
            .where(Image.deleted_at.is_(None))
        )

        if existing_image:
            print(f"Imagen ya existente, actualizando: {file.filename}")

            existing_image.filename = file.filename
            existing_image.extension = file.extension
            existing_image.url = file.url
            existing_image.user_id = file.user_id

            saved_image = existing_image

        else:
            print(f"Guardando nueva imagen: {file.filename}")

            saved_image = Image(
                filename=file.filename,
                extension=file.extension,
                url=file.url,
                user_id=file.user_id
            )

            db.add(saved_image)

        db.commit()
        db.refresh(saved_image)

        return saved_image

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar imagen: {str(e)}"
        )

async def save_mask(file: CreateFile, db: Session) -> Mask:
    try:
        existing_mask = db.scalar(
            select(Mask)
            .where(Mask.filename == file.filename)
            .where(Mask.deleted_at.is_(None))
        )

        if existing_mask:
            print(f"Máscara ya existente, actualizando: {file.filename}")

            existing_mask.filename = file.filename
            existing_mask.extension = file.extension
            existing_mask.url = file.url
            existing_mask.user_id = file.user_id

            saved_mask = existing_mask

        else:
            print(f"Guardando nueva máscara: {file.filename}")

            saved_mask = Mask(
                filename=file.filename,
                extension=file.extension,
                url=file.url,
                user_id=file.user_id
            )

            db.add(saved_mask)

        db.commit()
        db.refresh(saved_mask)

        return saved_mask

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar máscara: {str(e)}"
        )

async def save_image_mask(filename: str, db: Session) -> ImageMask:
    try:
        image, mask = await get_image_and_mask_by_filename(filename, db)

        existing_image_mask = db.scalar(
                    select(ImageMask)
                    .where(ImageMask.image_id == image.id)
                    .where(ImageMask.mask_id == mask.id)
                    .where(ImageMask.deleted_at.is_(None))
                )
        
        if existing_image_mask:
            print(f"Imagen Mascara ya existente, actualizando")

            existing_image_mask.image_id = image.id
            existing_image_mask.mask_id = mask.id

            saved_image_mask = existing_image_mask

        else:
            print(f"Guardando nueva imagen mascara: {filename}")

            saved_image_mask = ImageMask(
                image_id = image.id,
                mask_id = mask.id,
            )

            db.add(saved_image_mask)

        db.commit()
        db.refresh(saved_image_mask)

        return saved_image_mask

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar imagen: {str(e)}"
        )

async def save_object(file: CreateObject, db: Session) -> Object:
    try:
        existing_object = db.scalar(
            select(Object)
            .where(Object.filename == file.filename)
            .where(Object.deleted_at.is_(None))
        )

        if existing_object:
            print(f"Objeto ya existente, actualizando: {file.filename}")

            existing_object.filename = file.filename
            existing_object.extension = file.extension
            existing_object.url = file.url
            existing_object.image_mask_id = file.image_mask_id

            saved_object = existing_object

        else:
            print(f"Guardando nuevo objeto: {file.filename}")

            saved_object = Object(
                filename=file.filename,
                extension=file.extension,
                url=file.url,
                image_mask_id=file.image_mask_id
            )

            db.add(saved_object)

        db.commit()
        db.refresh(saved_object)

        return saved_object

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar Scaneo: {str(e)}"
        )

async def save_scanning(file: CreateModel, db: Session) -> Object:
    try:
        existing_scanning = db.scalar(
            select(Scanning)
            .where(Scanning.filename == file.filename)
            .where(Scanning.deleted_at.is_(None))
        )

        if existing_scanning:
            print(f"Scaneo ya existente, actualizando: {file.filename}")

            existing_scanning.filename = file.filename
            existing_scanning.extension = file.extension
            existing_scanning.url = file.url
            existing_scanning.object_id = file.object_id

            saved_scanning = existing_scanning

        else:
            print(f"Guardando nuevo Scaneo: {file.filename}")

            saved_scanning = Scanning(
                filename=file.filename,
                extension=file.extension,
                url=file.url,
                object_id=file.object_id
            )

            db.add(saved_scanning)

        db.commit()
        db.refresh(saved_scanning)

        return saved_scanning

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar escaneo: {str(e)}"
        )
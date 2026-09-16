from sqlalchemy import select

from app.core.security.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User
from app.db import base

def seed_users():
    db = SessionLocal()

    users_data = [
        {
            "names": "Animetx",
            "email": "animetx098@gmail.com",
            "password": "admin123",
        },
        {
            "names": "Brayan Polo",
            "email": "brayan@gmail.com",
            "password": "Brayan123!",
        },
        {
            "names": "Usuario Demo",
            "email": "demo@gmail.com",
            "password": "Demo123!",
        },
    ]

    try:
        for data in users_data:

            existing_user = db.scalar(
                select(User)
                .where(User.email == data["email"])
                .where(User.deleted_at.is_(None))
            )

            if existing_user:
                print(f"Usuario ya existe: {data['email']}")
                continue

            user = User(
                names=data["names"],
                email=data["email"],
                password=hash_password(data["password"]),
            )

            db.add(user)
            print(f"Creando usuario: {data['email']}")

        db.commit()

        print("Seeder ejecutado correctamente.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
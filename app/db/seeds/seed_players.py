from sqlalchemy import select
from app.core.security.security import hash_password
from app.db.database import SessionLocal
from app.models.player import Player
from app.models.user import User
from app.db import base

def seed_players():
    db = SessionLocal()
    players_data = [
        {
            "player_name": "Animetx",
            "user_id": "1"
        },
        {
            "player_name": "Elias123",
            "user_id": "2"
        },
        {
            "player_name": "Juan123",
            "user_id": "3"
        },
    ]

    try:
        for data in players_data:

            existing_user = db.scalar(
                select(User)
                .where(User.id == data["user_id"])
                .where(User.deleted_at.is_(None))
            )

            existing_player = db.scalar(
                select(Player)
                .where(Player.player_name == data["player_name"])
                .where(Player.deleted_at.is_(None))
            )

            if existing_player:
                print(f"Usuario ya tiene un jugador asignaod: {data['player_name']}")
                continue

            if not existing_user:
                print(f"usuario no encontrado: {data['user_id']}")
                continue
            
            player = Player(
                player_name=data["player_name"],
                user_id=data["user_id"],
            )

            db.add(player)
            print(f"Creando player: {data['player_name']}")

        db.commit()
        print("Seeder ejecutado correctamente.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_players()
"""
Seed the database with sample users and notes.

Run with:  python seed.py
Creates 5 users (password "password123" for all, for easy manual testing)
and a handful of notes for each.
"""
from faker import Faker

from config import app, db
from models import User, Note

fake = Faker()

SEED_PASSWORD = "password123"


def seed():
    with app.app_context():
        print("Clearing existing data...")
        Note.query.delete()
        User.query.delete()
        db.session.commit()

        print("Seeding users...")
        users = []
        # A predictable demo account, easy to log in with by hand.
        demo = User(username="demo")
        demo.password_hash = SEED_PASSWORD
        users.append(demo)

        for _ in range(4):
            user = User(username=fake.unique.user_name())
            user.password_hash = SEED_PASSWORD
            users.append(user)

        db.session.add_all(users)
        db.session.commit()

        print("Seeding notes...")
        notes = []
        for user in users:
            for _ in range(fake.random_int(min=3, max=8)):
                notes.append(
                    Note(
                        title=fake.sentence(nb_words=4).rstrip("."),
                        content=fake.paragraph(nb_sentences=3),
                        user_id=user.id,
                    )
                )
        db.session.add_all(notes)
        db.session.commit()

        print(f"Seeded {len(users)} users and {len(notes)} notes.")
        print(f"Demo login -> username: demo / password: {SEED_PASSWORD}")


if __name__ == "__main__":
    seed()

import os
import sqlite3

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "travel.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())

        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(user)")
        columns = {row[1] for row in cursor.fetchall()}
        if "balance_nrs" not in columns:
            cursor.execute(
                "ALTER TABLE user ADD COLUMN balance_nrs INTEGER NOT NULL DEFAULT 200000"
            )

        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        if user_count == 0:
            cursor.execute(
                """
                INSERT INTO user (name, email, password_hash, role, balance_nrs)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "Admin",
                    "admin@travel.com",
                    generate_password_hash("admin123"),
                    "admin",
                    0,
                ),
            )

        cursor.execute("SELECT COUNT(*) FROM destination")
        dest_count = cursor.fetchone()[0]
        if dest_count == 0:
            destinations = [
                (
                    "Bali Adventure",
                    20,
                    150000,
                    "20-day Bali trip with beach stays, temples, and island tours.",
                ),
                (
                    "Paris Highlights",
                    10,
                    300000,
                    "10-day Paris trip with museum passes and city excursions.",
                ),
                (
                    "Pokhara Escape",
                    5,
                    45000,
                    "5-day Pokhara trip with lakeside resorts and sunrise views.",
                ),
            ]
            cursor.executemany(
                "INSERT INTO destination (title, duration_days, price_nrs, description) VALUES (?, ?, ?, ?)",
                destinations,
            )

        connection.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)

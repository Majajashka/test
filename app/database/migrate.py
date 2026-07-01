from pathlib import Path

from app.database.connection import DB_PATH, get_connection

BASE_DIR = Path(__file__).parent

SCHEMA_FILES = [
    "schema_01_users.sql",
    "schema_02_images.sql",
    "schema_03_operations.sql",

]

SEED_FILE = "seed_data.sql"


def run_migrations(with_seed_data: bool = True) -> None:
    conn = get_connection()
    try:
        for filename in SCHEMA_FILES:
            sql_text = (BASE_DIR / filename).read_text(encoding="utf-8")
            conn.executescript(sql_text)

        if with_seed_data:
            seed_sql = (BASE_DIR / SEED_FILE).read_text(encoding="utf-8")
            conn.executescript(seed_sql)

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    if DB_PATH.exists():
        answer = input(f"{DB_PATH} უკვე არსებობს. გადავაწერო? (yes/no): ")
        if answer.strip().lower() != "yes":
            raise SystemExit(0)
        DB_PATH.unlink()

    run_migrations(with_seed_data=True)
    print(f"ბაზა მზადაა: {DB_PATH}")

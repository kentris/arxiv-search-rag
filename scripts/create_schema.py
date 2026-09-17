import os
import sys
import sqlite3

# Add project root directory to sys.path so 'config' can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config


def init_db():
    print(f"Initializing database at: {Config.DB_PATH}")

    # Determine script directory to locate create_schema.sql reliably
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Checks scripts/create_schema.sql first, then project root ../create_schema.sql
    schema_path = os.path.join(script_dir, "create_schema.sql")
    if not os.path.exists(schema_path):
        schema_path = os.path.join(script_dir, "..", "create_schema.sql")

    if not os.path.exists(schema_path):
        raise FileNotFoundError(
            f"Could not find 'create_schema.sql' in '{script_dir}' "
            f"or the parent project root directory."
        )

    print(f"Loading schema from: {schema_path}")

    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()

    print("SQLite database schema initialized successfully.")


if __name__ == "__main__":
    init_db()
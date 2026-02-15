
import sqlite3
from pathlib import Path

# Path to the database file
db_path = Path(__file__).parent.parent / "backend_dev.db"

print(f"Connecting to database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add shift_start column
    try:
        cursor.execute("ALTER TABLE doctors ADD COLUMN shift_start TEXT DEFAULT '09:00'")
        print("Added column: shift_start")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'shift_start' already exists.")
        else:
            print(f"Error adding 'shift_start': {e}")

    # Add shift_end column
    try:
        cursor.execute("ALTER TABLE doctors ADD COLUMN shift_end TEXT DEFAULT '17:00'")
        print("Added column: shift_end")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'shift_end' already exists.")
        else:
            print(f"Error adding 'shift_end': {e}")

    conn.commit()
    conn.close()
    print("Database schema update complete.")

except Exception as e:
    print(f"Database connection failed: {e}")

import sqlite3

conn = sqlite3.connect('backend_dev.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:")
for table in sorted(tables):
    print(f"  - {table}")

conn.close()

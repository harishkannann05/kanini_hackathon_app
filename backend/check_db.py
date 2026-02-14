import asyncio
import os
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Development overrides
DATABASE_URL_OVERRIDE = os.getenv("DATABASE_URL")
USE_SQLITE = os.getenv("USE_SQLITE", "0") == "1"

if DATABASE_URL_OVERRIDE:
    DATABASE_URL = DATABASE_URL_OVERRIDE
elif USE_SQLITE:
    DATABASE_URL = "sqlite+aiosqlite:///./backend_dev.db"
else:
    encoded_user = urllib.parse.quote_plus(USER or "")
    encoded_password = urllib.parse.quote_plus(PASSWORD or "")
    DATABASE_URL = f"postgresql+asyncpg://{encoded_user}:{encoded_password}@{HOST}:{PORT}/{DBNAME}"

# Connect args for asyncpg
connect_args = {}
if DATABASE_URL.startswith("postgresql+asyncpg"):
    connect_args = {"statement_cache_size": 0}

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=connect_args)

async def check():
    async with engine.connect() as conn:
        if DATABASE_URL.startswith("sqlite"):
            # Simple sqlite connectivity check
            r = await conn.execute(text("SELECT 1"))
            with open("constraints.txt", "w") as f:
                f.write("sqlite fallback — connectivity OK. No pg constraints to dump.\n")
            print("SQLite connectivity OK. Wrote constraints.txt (note: pg-specific checks skipped).")
            return

        # Postgres-specific constraint dump
        r = await conn.execute(text("""
            SELECT c.conrelid::regclass AS table_name, c.conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            WHERE c.contype = 'c'
            AND c.conrelid::regclass::text IN (
                'patients', 'visits', 'ai_assessments', 'doctors',
                'doctor_assignments', 'queue', 'documents', 'emergency_alerts',
                'notifications', 'audit_logs', 'departments', 'users'
            )
            ORDER BY c.conrelid::regclass::text, c.conname
        """))
        lines = []
        for row in r:
            lines.append(f"[{row[0]}] {row[1]}: {row[2]}")
        with open("constraints.txt", "w") as f:
            f.write("\n".join(lines))
        print(f"Written {len(lines)} constraints to constraints.txt")

asyncio.run(check())

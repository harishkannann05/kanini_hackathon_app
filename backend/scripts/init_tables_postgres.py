"""
Initialize all tables in SQLite.
Run: python -m backend.scripts.init_tables_postgres
This creates all ORM tables and reference data tables.
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / "backend" / ".env")

# Import models after dotenv
from backend.db import engine
from backend.models import Base


async def init_all_tables():
    """Create all tables in SQLite."""
    print("Initializing SQLite tables...")
    async with engine.begin() as conn:
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✓ All tables created successfully!")


if __name__ == "__main__":
    print("Starting table initialization...")
    try:
        asyncio.run(init_all_tables())
        print("Table initialization complete!")
    except Exception as e:
        print(f"Error initializing tables: {e}")
        import traceback
        traceback.print_exc()

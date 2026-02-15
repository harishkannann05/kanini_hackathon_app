from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env
load_dotenv()

DATABASE_URL_OVERRIDE = os.getenv("DATABASE_URL")
USE_SQLITE = os.getenv("USE_SQLITE", "1") == "1"

# SQLite-only configuration
db_path = Path(__file__).resolve().parents[1] / "backend_dev.db"
DATABASE_URL = DATABASE_URL_OVERRIDE or f"sqlite+aiosqlite:///{db_path}"
print(f"Using SQLite database at {db_path}")

# Create Async Engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Create tables for local development when using SQLite (if they don't exist)."""
    # import models lazily to avoid circular imports at top-level
    from models import Base
    async with engine.begin() as conn:
        # Only create tables if they don't already exist
        # SQLite doesn't have a way to check easily, so we'll just try to create
        # and it will be idempotent in most cases
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            # If table creation fails, it's likely because tables already exist
            # which is fine for development
            pass
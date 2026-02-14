from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from dotenv import load_dotenv
import os
import urllib.parse
from pathlib import Path

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")
# Allow explicit DATABASE_URL override (useful for connection strings)
DATABASE_URL_OVERRIDE = os.getenv("DATABASE_URL")
# Development fallback to SQLite when USE_SQLITE=1
USE_SQLITE = os.getenv("USE_SQLITE", "0") == "1"

if DATABASE_URL_OVERRIDE:
    DATABASE_URL = DATABASE_URL_OVERRIDE
    print(f"Using DATABASE_URL override: {DATABASE_URL}")
elif USE_SQLITE:
    # Local development sqlite file - use absolute path from project root
    db_path = Path(__file__).resolve().parents[1] / "backend_dev.db"
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
    print(f"Using SQLite development mode at {db_path}")
else:
    # PostgreSQL / Supabase
    if not (USER and PASSWORD and HOST and PORT and DBNAME):
        print("Warning: Incomplete PostgreSQL credentials in .env")
        print(f"  user={USER}, password={'***' if PASSWORD else 'MISSING'}, host={HOST}, port={PORT}, dbname={DBNAME}")

    # URL-encode credentials to handle special characters (like '@' in password)
    encoded_user = urllib.parse.quote_plus(USER or "")
    encoded_password = urllib.parse.quote_plus(PASSWORD or "")

    # Construct Database URL
    DATABASE_URL = f"postgresql+asyncpg://{encoded_user}:{encoded_password}@{HOST}:{PORT}/{DBNAME}"
    print(f"Connecting to PostgreSQL at {HOST}:{PORT}")

# Create Async Engine
# For PostgreSQL (asyncpg) we disable prepared statements for Supabase pooler.
engine_kwargs = {"echo": False}
connect_args = {}
if DATABASE_URL.startswith("postgresql+asyncpg"):
    connect_args = {"statement_cache_size": 0}

if connect_args:
    engine = create_async_engine(DATABASE_URL, **engine_kwargs, connect_args=connect_args)
else:
    engine = create_async_engine(DATABASE_URL, **engine_kwargs)

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
    if not USE_SQLITE:
        return
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
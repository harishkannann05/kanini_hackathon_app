from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from dotenv import load_dotenv
import os
import urllib.parse

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

if PASSWORD == "[YOUR-PASSWORD]":
    print("Error: Please replace '[YOUR-PASSWORD]' in backend/.env with your actual Supabase database password.")
    exit(1)

# URL-encode credentials to handle special characters (like '@' in password)
encoded_user = urllib.parse.quote_plus(USER)
encoded_password = urllib.parse.quote_plus(PASSWORD)

# Construct Database URL
DATABASE_URL = f"postgresql+asyncpg://{encoded_user}:{encoded_password}@{HOST}:{PORT}/{DBNAME}"

# Create Async Engine
# Note: For Supabase transaction pooler (port 6543), we must disable prepared statements
# by setting statement_cache_size to 0.
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"statement_cache_size": 0}
)

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

"""SQLite setup wrapper - use migrate_db for full initialization."""
import asyncio
from backend.scripts.migrate_db import main


if __name__ == "__main__":
    asyncio.run(main())

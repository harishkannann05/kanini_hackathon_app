import asyncio
from sqlalchemy import text
from db import engine

async def check():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
        lines = ["sqlite connectivity OK"]
        with open("constraints.txt", "w") as f:
            f.write("\n".join(lines))
        print("SQLite connectivity OK. Wrote constraints.txt.")

asyncio.run(check())

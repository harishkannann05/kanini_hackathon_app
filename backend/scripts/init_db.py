import asyncio

async def run():
    from backend.db import init_db
    await init_db()
    print('init_db completed')

if __name__ == '__main__':
    asyncio.run(run())

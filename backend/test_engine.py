"""Test SQLAlchemy engine"""
import asyncio
from sqlalchemy import Column, Integer, String, Table, MetaData, inspect
from db import engine

async def test_engine():
    print("Testing SQLAlchemy engine...")
    
    # Get engine URL
    print(f"Engine URL: {engine.url}")
    
    # Try to create a simple table
    metadata = MetaData()
    
    test_table = Table(
        'test_table',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50))
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
        print("✓ Test table created")
        
        # Verify
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        print(f"Tables after create_all: {tables}")
        
        # Drop test table
        await conn.run_sync(metadata.drop_all)
        print("✓ Test table dropped")

if __name__ == "__main__":
    asyncio.run(test_engine())

import asyncio
import os
import sys

from app.db.engine import async_engine
from sqlalchemy import text

async def test():
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Connection successful! Result:", result.scalar())
    except Exception as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    asyncio.run(test())

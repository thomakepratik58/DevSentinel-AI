import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    urls = [
        "postgresql+asyncpg://devsentinel@localhost:5432/devsentinel",
        "postgresql+asyncpg://postgres@localhost:5432/postgres",
    ]
    for url in urls:
        print(f"Testing {url}")
        engine = create_async_engine(url)
        try:
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                print("SUCCESS:", url)
        except Exception as e:
            print("FAILED")
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test())

import asyncpg
from config import NEON_DATABASE_URL

async def setup_db():
    conn = await asyncpg.connect(NEON_DATABASE_URL)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            sku TEXT PRIMARY KEY,
            name TEXT,
            price REAL,
            last_updated TIMESTAMP
        )
    """)

    return conn
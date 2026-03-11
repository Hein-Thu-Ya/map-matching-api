import asyncpg
from app.core.config import settings

pool = None


async def connect_db():
    global pool

    pool = await asyncpg.create_pool(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        min_size=5,
        max_size=20
    )


async def get_pool():
    return pool
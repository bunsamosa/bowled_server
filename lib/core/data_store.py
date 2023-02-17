import os

import asyncpg


# READ postgres url from env
POSTGRES_URL = os.getenv(
    key="POSTGRES_URL",
    default=None,
)


async def get_connection_pool() -> asyncpg.pool.Pool:
    """
    Connect to postgres and return connection pool
    :return: Connection pool
    """
    if not POSTGRES_URL:
        raise ValueError("Invalid POSTGRES_URL")

    return await asyncpg.create_pool(dsn=POSTGRES_URL)

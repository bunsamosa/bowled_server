from dataclasses import dataclass

import asyncpg
import structlog

from lib.core.cache_store import CacheStore


@dataclass
class Context:
    """
    Context class represents essential connectors for each request.
    :param logger: structlog logger
    :param request_id: string request ID
    :param cachestore: CacheStore connector
    :param data_store: Datastore connector instance
    :param ds_connection: Datastore connection instance
    """

    logger: structlog.stdlib.AsyncBoundLogger
    request_id: str
    cachestore: CacheStore
    data_store: asyncpg.pool.Pool
    ds_connection: asyncpg.pool.PoolAcquireContext = None

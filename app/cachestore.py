from typing import Optional

import redis
from pottery import RedisDict


# Read redis host from env
REDIS_HOST = "redis://127.0.0.1:6379/0"


class CacheStore:
    """
    Redis cache store
    This module is used to store key values in the cache store.
    """

    def __init__(self, namespace: str) -> None:
        """
        Connect to redis client
        Raises exception if unable to connect to redis
        """
        redis_client = redis.from_url(REDIS_HOST)

        # Validate string namespace
        if not isinstance(namespace, str):
            raise Exception("Invalid namespace")
        namespace = namespace.strip()
        if not namespace:
            raise Exception("Invalid namespace")
        self.__namespace = namespace

        # Check if client is connected to redis
        if redis_client.ping():
            self.__client: redis.Redis = redis_client
        else:
            raise Exception("Unable to connect to redis")

    def is_connected(self) -> bool:
        """
        Check if client is connected to redis
        :return: True if connected else False
        """
        return self.__client.ping()

    def get_dictionary(self, key: str) -> Optional[dict]:
        """
        Get a dictionary stored in redis
        :param key: Key to get dictionary for
        :return: Dictionary for the key
        """
        if not isinstance(key, str):
            raise Exception("Invalid key")

        key = key.strip()
        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        value = RedisDict(key=key, redis=self.__client)
        return value

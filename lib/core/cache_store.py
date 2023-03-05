import os
from typing import Optional

import redis
from pottery import NextId
from pottery import RedisDict


# Read redis host from env
REDIS_HOST = os.getenv(key="REDIS_HOST", default="redis://127.0.0.1:6379/0")


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
            raise ValueError("Invalid namespace")

        namespace = namespace.strip()
        if not namespace:
            raise ValueError("Invalid namespace")
        self.__namespace = namespace

        # Check if client is connected to redis
        if not redis_client.ping():
            raise ConnectionError("Unable to connect to redis")

        self.__client: redis.Redis = redis_client

    def is_connected(self) -> bool:
        """
        Check if client is connected to redis
        :return: True if connected else False
        """
        return self.__client.ping()

    def get_key(self, key: str) -> Optional[str]:
        """
        Fetch value for the key from redis cache
        :param key: Key to fetch value for
        :return: Value for the key
        """
        # Validate string key
        if not isinstance(key, str):
            return None

        key = key.strip()
        if not key:
            return None

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return self.__client.get(key)

    def set_key(
        self,
        key: str,
        value: str,
        expire: Optional[int] = 300,
    ) -> Optional[bool]:
        """
        Set value for the key in redis cache
        :param key: Key to set value for
        :param value: Value to set
        :param expire: Expire time in seconds (minimum 1 second, maximum 1 day)
        :return: True if set else False
        """
        if (
            not isinstance(key, str)
            or not isinstance(value, str)
            or not isinstance(expire, int)
        ):
            raise ValueError("Invalid parameter")

        key = key.strip()
        value = value.strip()
        if not key or not value or not 0 < expire < 86400:
            raise ValueError("Invalid parameter")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return self.__client.setex(name=key, value=value, time=expire)

    def delete_key(self, key: str) -> Optional[int]:
        """
        Delete key:value from redis cache
        :param key: Key to delete
        """
        # Validate string key
        if not isinstance(key, str):
            raise ValueError("Invalid key")

        key = key.strip()
        if not key:
            raise ValueError("Invalid key")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return self.__client.delete(key)

    def get_dictionary(self, key: str) -> RedisDict:
        """
        Get a dictionary stored in redis
        :param key: Key to get dictionary for
        :return: Dictionary for the key
        """
        if not isinstance(key, str):
            raise ValueError("Invalid key")

        key = key.strip()
        if not key:
            raise ValueError("Invalid key")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        value = RedisDict(key=key, redis=self.__client)
        return value

    def get_id_generator(self, key: str):
        """
        Get a unique ID generator
        """
        if not isinstance(key, str):
            raise ValueError("Invalid key")

        key = key.strip()
        if not key:
            raise ValueError("Invalid key")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return NextId(key=key, masters={self.__client})

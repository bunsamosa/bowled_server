from pydantic import BaseModel


class HeartBeat(BaseModel):
    """
    JSON schema for the return data
    """

    datastore_connected: bool = False
    cachestore_connected: bool = False
    errors: dict = {}

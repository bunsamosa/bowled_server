from dataclasses import dataclass


@dataclass
class HTTPError:
    """
    HTTPError class represents an HTTP error
    """

    error_code: int
    error_msg: str

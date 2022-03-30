from typing import Optional

from redis.client import Redis
from rq import Connection

from emischeduler.config import config


def get_redis_client() -> Redis:
    return Redis(
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_password,
    )


def make_url(
    host: str,
    port: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    if username is None and password is None:
        return f"redis://{host}:{port}"
    return f"redis://{username or ''}:{password or ''}@{host}:{port}"

from typing import Optional

from redis.client import Redis

from emischeduler.config.models import RedisConfig


def get_redis_client(config: RedisConfig) -> Redis:
    return Redis(host=config.host, port=config.port, password=config.password)


def make_url(
    host: str,
    port: int,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    if username is None and password is None:
        return f"redis://{host}:{port}"
    return f"redis://{username or ''}:{password or ''}@{host}:{port}"

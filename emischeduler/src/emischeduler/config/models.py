from pydantic import BaseModel

from emischeduler.config.base import BaseConfig


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 32000
    password: str = "password"


class AdminConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 33000
    username: str = "admin"
    password: str = "password"


class EmistreamConfig(BaseConfig):
    host: str = "localhost"
    port: int = 10000


class EmiarchiveConfig(BaseConfig):
    host: str = "localhost"
    port: int = 30000
    username: str = "readonly"
    password: str = "password"


class EmishowsConfig(BaseConfig):
    host: str = "localhost"
    port: int = 35000


class Config(BaseConfig):
    redis: RedisConfig = RedisConfig()
    admin: AdminConfig = AdminConfig()
    emistream: EmistreamConfig = EmistreamConfig()
    emiarchive: EmiarchiveConfig = EmiarchiveConfig()
    emishows: EmishowsConfig = EmishowsConfig()

import os

from pydantic import BaseModel


class Config(BaseModel):
    redis_host: str = os.getenv("EMISCHEDULER_DB_HOST", "localhost")
    redis_port: int = int(os.getenv("EMISCHEDULER_DB_PORT", 32000))
    redis_password: str = os.getenv("EMISCHEDULER_DB_PASSWORD", "password")
    admin_host: str = os.getenv("EMISCHEDULER_ADMIN_HOST", "0.0.0.0")
    admin_port: int = int(os.getenv("EMISCHEDULER_ADMIN_PORT", 33000))
    admin_username: str = os.getenv("EMISCHEDULER_ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("EMISCHEDULER_ADMIN_PASSWORD", "password")
    emistream_host: str = os.getenv("EMISCHEDULER_EMISTREAM_HOST", "localhost")
    emistream_port: int = int(os.getenv("EMISCHEDULER_EMISTREAM_PORT", 10000))
    emiarchive_host: str = os.getenv(
        "EMISCHEDULER_EMIARCHIVE_HOST", "localhost"
    )
    emiarchive_port: int = int(
        os.getenv("EMISCHEDULER_EMIARCHIVE_PORT", 30000)
    )
    emiarchive_username: str = os.getenv(
        "EMISCHEDULER_EMIARCHIVE_USERNAME", "readonly"
    )
    emiarchive_password: str = os.getenv(
        "EMISCHEDULER_EMIARCHIVE_PASSWORD", "password"
    )
    emishows_host: str = os.getenv("EMISCHEDULER_EMISHOWS_HOST", "localhost")
    emishows_port: int = int(os.getenv("EMISCHEDULER_EMISHOWS_PORT", 35000))


config = Config()

from pathlib import Path

from pydantic import BaseModel

from emischeduler.config.base import BaseConfig


class ApiConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 33000


class EmistreamConfig(BaseModel):
    host: str = "localhost"
    port: int = 10000


class EmiarchiveConfig(BaseModel):
    host: str = "localhost"
    port: int = 30000
    username: str = "readonly"
    password: str = "password"
    secure: bool = False


class EmishowsConfig(BaseModel):
    host: str = "localhost"
    port: int = 35000


class Config(BaseConfig):
    api: ApiConfig = ApiConfig()
    emistream: EmistreamConfig = EmistreamConfig()
    emiarchive: EmiarchiveConfig = EmiarchiveConfig()
    emishows: EmishowsConfig = EmishowsConfig()
    log_file: Path = Path("log.csv")
    live_recordings_bucket: str = "live-recordings"
    pre_recorded_bucket: str = "pre-recorded"

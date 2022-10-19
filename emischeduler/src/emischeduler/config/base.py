from typing import Tuple

from pydantic import BaseSettings, Extra
from pydantic.env_settings import SettingsSourceCallable


class BaseConfig(BaseSettings):
    class Config:
        env_prefix = "emischeduler_"
        env_nested_delimiter = "__"
        env_file = ".env"
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings

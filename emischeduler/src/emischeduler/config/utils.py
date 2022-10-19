from typing import Optional, TextIO, Iterable

from omegaconf import OmegaConf

from emischeduler import resource_text
from emischeduler.config.models import Config


def get_config(
    f: Optional[TextIO] = None, overrides: Optional[Iterable[str]] = None
) -> Config:
    config = OmegaConf.create(resource_text("config.yaml"))
    if f is not None:
        config = OmegaConf.merge(config, OmegaConf.load(f))
    if overrides is not None:
        config = OmegaConf.merge(
            config, OmegaConf.from_dotlist(list(overrides))
        )
    config = OmegaConf.to_container(config, resolve=True)
    return Config.parse_obj(config)

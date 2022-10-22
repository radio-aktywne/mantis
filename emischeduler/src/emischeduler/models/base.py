import json
from abc import ABC
from datetime import datetime
from typing import Dict, Any

from humps.main import camelize
from pydantic import BaseModel

from emischeduler.hashing import hashify
from emischeduler.time import stringify


class SerializableModel(BaseModel, ABC):
    def json(self, *args, by_alias: bool = True, **kwargs) -> str:
        return super().json(*args, by_alias=by_alias, **kwargs)

    def dict(self, *args, by_alias: bool = True, **kwargs):
        return self.json_dict(*args, by_alias=by_alias, **kwargs)

    def json_dict(self, *args, **kwargs) -> Dict[str, Any]:
        return json.loads(self.json(*args, **kwargs))

    def __hash__(self) -> int:
        return hashify(self.json(sort_keys=True))

    class Config:
        allow_population_by_field_name = True
        alias_generator = camelize
        json_encoders = {datetime: stringify}

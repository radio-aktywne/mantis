from pathlib import Path
from typing import List

from minio import Minio
from minio.datatypes import Object

from emischeduler.utils import background


class ArchiveClient:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._client = Minio(*args, **kwargs)

    async def list(self, bucket: str, prefix: str) -> List[Object]:
        def _list(_bucket: str, _prefix: str) -> List[Object]:
            return list(self._client.list_objects(_bucket, prefix=_prefix))

        return await background(_list, bucket, prefix)

    async def download(self, bucket: str, key: str, path: str | Path) -> None:
        return await background(
            self._client.fget_object, bucket, key, str(path)
        )

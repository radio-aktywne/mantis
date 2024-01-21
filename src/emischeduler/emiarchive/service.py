import asyncio

from minio import Minio
from minio.datatypes import Object
from minio.error import MinioException

from emischeduler.config.models import EmiarchiveConfig
from emischeduler.emiarchive import errors as e
from emischeduler.emiarchive import models as m


class BucketReader:
    """Reads objects from a bucket."""

    def __init__(self, client: Minio, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def _map_object(self, object: Object) -> m.Object:
        return m.Object(
            bucket=object.bucket_name,
            name=object.object_name,
            modified=object.last_modified,
            etag=object.etag,
            size=object.size,
            metadata=object.metadata,
            content_type=object.content_type,
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get an object."""

        try:
            object = await asyncio.to_thread(
                self._client.stat_object,
                bucket_name=self._bucket,
                object_name=request.name,
            )
        except (ValueError, TypeError, MinioException) as ex:
            raise e.EmiarchiveError(message=str(ex)) from ex

        object = self._map_object(object)
        return m.GetResponse(object=object)

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List objects."""

        try:
            objects = await asyncio.to_thread(
                self._client.list_objects,
                bucket_name=self._bucket,
                prefix=request.prefix,
                recursive=request.recursive,
            )
        except (ValueError, TypeError, MinioException) as ex:
            raise e.EmiarchiveError(message=str(ex)) from ex

        objects = [self._map_object(object) for object in objects]
        return m.ListResponse(objects=objects)

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download an object."""

        try:
            object = await asyncio.to_thread(
                self._client.fget_object,
                bucket_name=self._bucket,
                object_name=request.name,
                file_path=str(request.path),
            )
        except (ValueError, TypeError, MinioException) as ex:
            raise e.EmiarchiveError(message=str(ex)) from ex

        object = self._map_object(object)
        return m.DownloadResponse(object=object)


class EmiarchiveService:
    """Service for emiarchive."""

    def __init__(self, config: EmiarchiveConfig) -> None:
        client = Minio(
            endpoint=f"{config.host}:{config.port}",
            access_key=config.user,
            secret_key=config.password,
            secure=False,
            cert_check=False,
        )
        self._live = BucketReader(client, config.live_bucket)
        self._prerecorded = BucketReader(client, config.prerecorded_bucket)

    @property
    def live(self) -> BucketReader:
        """Get the live bucket reader."""

        return self._live

    @property
    def prerecorded(self) -> BucketReader:
        """Get the prerecorded bucket reader."""

        return self._prerecorded

import asyncio
from collections.abc import Generator
from contextlib import contextmanager
from enum import StrEnum

from minio import Minio
from minio.datatypes import Object
from minio.error import MinioException, S3Error
from urllib3 import BaseHTTPResponse

from emischeduler.config.models import DatarecordsConfig
from emischeduler.services.datarecords import errors as e
from emischeduler.services.datarecords import models as m
from emischeduler.utils import asyncify
from emischeduler.utils.time import httpparse


class ErrorCodes(StrEnum):
    """Error codes."""

    NOT_FOUND = "NoSuchKey"


class BucketReader:
    """Utility class for reading objects from a bucket."""

    def __init__(self, client: Minio, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def _map_object(self, object: Object) -> m.Object:
        return m.Object(
            name=object.object_name,
            modified=object.last_modified,
            size=object.size,
            metadata=object.metadata,
            type=object.content_type,
        )

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except MinioException as ex:
            raise e.ServiceError(str(ex)) from ex

    @contextmanager
    def _handle_not_found(self, name: str) -> Generator[None]:
        try:
            yield
        except S3Error as ex:
            if ex.code == ErrorCodes.NOT_FOUND:
                raise e.NotFoundError(name) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List objects."""

        bucket = self._bucket
        prefix = request.prefix
        recursive = request.recursive

        with self._handle_errors():
            objects = await asyncio.to_thread(
                self._client.list_objects,
                bucket_name=bucket,
                prefix=prefix,
                recursive=recursive,
            )

        objects = (self._map_object(object) for object in objects)
        objects = asyncify.iterator(objects)

        return m.ListResponse(
            objects=objects,
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get an object."""

        bucket = self._bucket
        name = request.name

        with self._handle_errors():
            with self._handle_not_found(name):
                object = await asyncio.to_thread(
                    self._client.stat_object,
                    bucket_name=bucket,
                    object_name=name,
                )

        object = self._map_object(object)

        return m.GetResponse(
            object=object,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download an object."""

        bucket = self._bucket
        name = request.name

        with self._handle_errors():
            with self._handle_not_found(name):
                res = await asyncio.to_thread(
                    self._client.get_object,
                    bucket_name=bucket,
                    object_name=name,
                )

        def _data(res: BaseHTTPResponse, chunk: int) -> Generator[bytes]:
            try:
                yield from res.stream(chunk)
            finally:
                res.close()
                res.release_conn()

        type = res.headers["Content-Type"]
        size = int(res.headers["Content-Length"])
        tag = res.headers["ETag"]
        modified = httpparse(res.headers["Last-Modified"])

        chunk = request.chunk
        data = asyncify.iterator(_data(res, chunk))

        content = m.DownloadContent(
            type=type,
            size=size,
            tag=tag,
            modified=modified,
            data=data,
        )
        return m.DownloadResponse(
            content=content,
        )


class DatarecordsService:
    """Service for datarecords database."""

    def __init__(self, config: DatarecordsConfig) -> None:
        client = Minio(
            endpoint=config.s3.endpoint,
            access_key=config.s3.user,
            secret_key=config.s3.password,
            secure=config.s3.secure,
            cert_check=False,
        )
        self._live = BucketReader(client, config.s3.live_bucket)
        self._prerecorded = BucketReader(client, config.s3.prerecorded_bucket)

    @property
    def live(self) -> BucketReader:
        """Live bucket reader."""

        return self._live

    @property
    def prerecorded(self) -> BucketReader:
        """Prerecorded bucket reader."""

        return self._prerecorded

from datetime import datetime
from pathlib import Path

from pydantic import Field

from emischeduler.models.base import SerializableModel


class Object(SerializableModel):
    """Object model."""

    bucket: str = Field(
        ...,
        title="Object.Bucket",
        description="Bucket name.",
    )
    name: str = Field(
        ...,
        title="Object.Name",
        description="Object name.",
    )
    modified: datetime | None = Field(
        ...,
        title="Object.Modified",
        description="Time when the object was last modified.",
    )
    etag: str | None = Field(
        ...,
        title="Object.Etag",
        description="ETag of the object.",
    )
    size: int | None = Field(
        ...,
        title="Object.Size",
        description="Size of the object.",
    )
    metadata: dict[str, str] | None = Field(
        ...,
        title="Object.Metadata",
        description="Metadata of the object.",
    )
    content_type: str | None = Field(
        ...,
        title="Object.ContentType",
        description="Content type of the object.",
    )


class GetRequest(SerializableModel):
    """Request for getting an object."""

    name: str = Field(
        ...,
        title="GetRequest.Name",
        description="Name of the object to get.",
    )


class GetResponse(SerializableModel):
    """Response for getting an object."""

    object: Object = Field(
        ...,
        title="GetResponse.Object",
        description="Object.",
    )


class ListRequest(SerializableModel):
    """Request for listing objects."""

    prefix: str | None = Field(
        None,
        title="ListRequest.Prefix",
        description="Prefix of the objects to list.",
    )
    recursive: bool = Field(
        True,
        title="ListRequest.Recursive",
        description="Whether to list objects recursively.",
    )


class ListResponse(SerializableModel):
    """Response for listing objects."""

    objects: list[Object] = Field(
        ...,
        title="ListResponse.Objects",
        description="List of objects.",
    )


class DownloadRequest(SerializableModel):
    """Request for downloading an object."""

    name: str = Field(
        ...,
        title="DownloadRequest.Name",
        description="Name of the object to download.",
    )
    path: Path = Field(
        ...,
        title="DownloadRequest.Path",
        description="Path to download the object to.",
    )


class DownloadResponse(SerializableModel):
    """Response for downloading an object."""

    object: Object = Field(
        ...,
        title="DownloadResponse.Object",
        description="Downloaded object.",
    )

from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, Field, NaiveDatetime

from emischeduler.config.base import BaseConfig


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = Field(
        "0.0.0.0",
        title="Host",
        description="Host to run the server on.",
    )
    port: int = Field(
        33000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to run the server on.",
    )


class StoreConfig(BaseModel):
    """Configuration for the store."""

    path: Path = Field(
        Path("data/state.json"),
        title="Path",
        description="Path to the store file.",
    )


class StreamConfig(BaseModel):
    """Configuration for the stream operation."""

    timeout: timedelta = Field(
        timedelta(hours=1),
        title="Timeout",
        description="Timeout for trying to reserve a stream.",
    )


class CleanerConfig(BaseModel):
    """Configuration for the cleaner."""

    reference: NaiveDatetime = Field(
        datetime(2000, 1, 1, 0, 0, 0, 0),
        title="Reference",
        description="Reference datetime for cleaning.",
    )
    interval: timedelta = Field(
        timedelta(days=1),
        title="Interval",
        description="Interval between cleanings.",
    )


class StreamSynchronizerConfig(BaseModel):
    """Configuration for the stream synchronizer."""

    window: timedelta = Field(
        timedelta(days=1),
        title="Window",
        description="Duration of the time window.",
    )


class SynchronizerConfig(BaseModel):
    """Configuration for the synchronizer."""

    reference: NaiveDatetime = Field(
        datetime(2000, 1, 1, 0, 0, 0, 0),
        title="Reference",
        description="Reference datetime for synchronization.",
    )
    interval: timedelta = Field(
        timedelta(minutes=1),
        title="Interval",
        description="Interval between synchronizations.",
    )
    stream: StreamSynchronizerConfig = Field(
        StreamSynchronizerConfig(),
        title="Stream",
        description="Configuration for the stream synchronizer.",
    )


class EmishowsHTTPConfig(BaseModel):
    """Configuration for the Emishows HTTP API."""

    scheme: str = Field(
        "http",
        title="Scheme",
        description="Scheme of the HTTP API.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the HTTP API.",
    )
    port: int | None = Field(
        35000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the HTTP API.",
    )
    path: str | None = Field(
        None,
        title="Path",
        description="Path of the HTTP API.",
    )

    @property
    def url(self) -> str:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmishowsConfig(BaseModel):
    """Configuration for the Emishows service."""

    http: EmishowsHTTPConfig = Field(
        EmishowsHTTPConfig(),
        title="HTTP",
        description="Configuration for the HTTP API.",
    )


class DatarecordsS3Config(BaseModel):
    """Configuration for the Datarecords S3 API."""

    secure: bool = Field(
        False,
        title="Secure",
        description="Whether to use a secure connection.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the S3 API.",
    )
    port: int | None = Field(
        30000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the S3 API.",
    )
    user: str = Field(
        "readonly",
        title="User",
        description="Username to authenticate with the S3 API.",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to authenticate with the S3 API.",
    )
    live_bucket: str = Field(
        "live",
        title="LiveBucket",
        description="Name of the bucket with recordings of live events.",
    )
    prerecorded_bucket: str = Field(
        "prerecorded",
        title="PrerecordedBucket",
        description="Name of the bucket with prerecorded events.",
    )


class DatarecordsConfig(BaseModel):
    """Configuration for the Datarecords database."""

    s3: DatarecordsS3Config = Field(
        DatarecordsS3Config(),
        title="S3",
        description="Configuration for the S3 API.",
    )


class EmistreamHTTPConfig(BaseModel):
    """Configuration for the Emistream HTTP API."""

    scheme: str = Field(
        "http",
        title="Scheme",
        description="Scheme of the HTTP API.",
    )
    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the HTTP API.",
    )
    port: int | None = Field(
        10000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the HTTP API.",
    )
    path: str | None = Field(
        None,
        title="Path",
        description="Path of the HTTP API.",
    )

    @property
    def url(self) -> str:
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmistreamSRTConfig(BaseModel):
    """Configuration for the Emistream SRT stream."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host of the SRT stream.",
    )
    port: int = Field(
        10000,
        ge=1,
        le=65535,
        title="Port",
        description="Port of the SRT stream.",
    )

    @property
    def url(self) -> str:
        return f"srt://{self.host}:{self.port}"


class EmistreamConfig(BaseModel):
    """Configuration for the Emistream service."""

    http: EmistreamHTTPConfig = Field(
        EmistreamHTTPConfig(),
        title="HTTP",
        description="Configuration for the HTTP API.",
    )
    srt: EmistreamSRTConfig = Field(
        EmistreamSRTConfig(),
        title="SRT",
        description="Configuration for the SRT stream.",
    )


class Config(BaseConfig):
    """Configuration for the application."""

    server: ServerConfig = Field(
        ServerConfig(),
        title="Server",
        description="Configuration for the server.",
    )
    store: StoreConfig = Field(
        StoreConfig(),
        title="Store",
        description="Configuration for the store.",
    )
    stream: StreamConfig = Field(
        StreamConfig(),
        title="Stream",
        description="Configuration for the stream operation.",
    )
    cleaner: CleanerConfig = Field(
        CleanerConfig(),
        title="Cleaner",
        description="Configuration for the cleaner.",
    )
    synchronizer: SynchronizerConfig = Field(
        SynchronizerConfig(),
        title="Synchronizer",
        description="Configuration for the synchronizer.",
    )
    emishows: EmishowsConfig = Field(
        EmishowsConfig(),
        title="Emishows",
        description="Configuration for the Emishows service.",
    )
    datarecords: DatarecordsConfig = Field(
        DatarecordsConfig(),
        title="Datarecords",
        description="Configuration for the Datarecords database.",
    )
    emistream: EmistreamConfig = Field(
        EmistreamConfig(),
        title="Emistream",
        description="Configuration for the Emistream service.",
    )

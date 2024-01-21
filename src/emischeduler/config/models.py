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
        "data/state.json",
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
    window: timedelta = Field(
        timedelta(days=1),
        title="Window",
        description="Duration of the time window.",
    )


class EmishowsConfig(BaseModel):
    """Configuration for the Emishows service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        35000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )


class EmiarchiveConfig(BaseModel):
    """Configuration for the Emiarchive service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        30000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
    )
    user: str = Field(
        "readonly",
        title="User",
        description="Username to connect with.",
    )
    password: str = Field(
        "password",
        title="Password",
        description="Password to connect with.",
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


class EmistreamConfig(BaseModel):
    """Configuration for the Emistream service."""

    host: str = Field(
        "localhost",
        title="Host",
        description="Host to connect to.",
    )
    port: int = Field(
        10000,
        ge=0,
        le=65535,
        title="Port",
        description="Port to connect to.",
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
    emiarchive: EmiarchiveConfig = Field(
        EmiarchiveConfig(),
        title="Emiarchive",
        description="Configuration for the Emiarchive service.",
    )
    emistream: EmistreamConfig = Field(
        EmistreamConfig(),
        title="Emistream",
        description="Configuration for the Emistream service.",
    )

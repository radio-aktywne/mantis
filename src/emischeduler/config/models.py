from datetime import datetime, timedelta
from pathlib import Path
from socket import gethostbyname

from pydantic import BaseModel, Field

from emischeduler.config.base import BaseConfig
from emischeduler.utils.time import NaiveDatetime


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    port: int = Field(33000, ge=0, le=65535)
    """Port to run the server on."""

    trusted: str | list[str] | None = "*"
    """Trusted IP addresses."""


class StoreConfig(BaseModel):
    """Configuration for the store."""

    path: Path = Path("data/state.json")
    """Path to the store file."""


class StreamConfig(BaseModel):
    """Configuration for the stream operation."""

    timeout: timedelta = timedelta(hours=1)
    """Timeout for trying to reserve a stream."""

    window: timedelta = timedelta(days=60)
    """Duration of the time window for searching for past records."""


class OperationsConfig(BaseModel):
    """Configuration for the operations."""

    stream: StreamConfig = StreamConfig()
    """Configuration for the stream operation."""


class CleanerConfig(BaseModel):
    """Configuration for the cleaner."""

    reference: NaiveDatetime = datetime(2000, 1, 1, 0, 0, 0, 0)
    """Reference datetime for cleaning."""

    interval: timedelta = timedelta(days=1)
    """Interval between cleanings."""


class StreamSynchronizerConfig(BaseModel):
    """Configuration for the stream synchronizer."""

    window: timedelta = timedelta(days=1)
    """Duration of the time window."""


class SynchronizersConfig(BaseModel):
    """Configuration for the synchronizers."""

    stream: StreamSynchronizerConfig = StreamSynchronizerConfig()
    """Configuration for the stream synchronizer."""


class SynchronizerConfig(BaseModel):
    """Configuration for the synchronizer."""

    reference: NaiveDatetime = datetime(2000, 1, 1, 0, 0, 0, 0)
    """Reference datetime for synchronization."""

    interval: timedelta = timedelta(minutes=1)
    """Interval between synchronizations."""

    synchronizers: SynchronizersConfig = SynchronizersConfig()
    """Configuration for the synchronizers."""


class EmiloungeHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the emilounge service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(28000, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""

        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmiloungeConfig(BaseModel):
    """Configuration for the emilounge service."""

    http: EmiloungeHTTPConfig = EmiloungeHTTPConfig()
    """Configuration for the HTTP API."""


class EmirecordsHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the emirecords service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(31000, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""

        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmirecordsConfig(BaseModel):
    """Configuration for the emirecords service."""

    http: EmirecordsHTTPConfig = EmirecordsHTTPConfig()
    """Configuration for the HTTP API."""


class EmishowsHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the emishows service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(35000, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""

        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmishowsConfig(BaseModel):
    """Configuration for the emishows service."""

    http: EmishowsHTTPConfig = EmishowsHTTPConfig()
    """Configuration for the HTTP API."""


class EmistreamHTTPConfig(BaseModel):
    """Configuration for the HTTP API of the emistream service."""

    scheme: str = "http"
    """Scheme of the HTTP API."""

    host: str = "localhost"
    """Host of the HTTP API."""

    port: int | None = Field(10000, ge=1, le=65535)
    """Port of the HTTP API."""

    path: str | None = None
    """Path of the HTTP API."""

    @property
    def url(self) -> str:
        """URL of the HTTP API."""

        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        if self.path:
            path = self.path if self.path.startswith("/") else f"/{self.path}"
            path = path.rstrip("/")
            url = f"{url}{path}"
        return url


class EmistreamSRTConfig(BaseModel):
    """Configuration for the SRT stream of the emistream service."""

    host: str = "localhost"
    """Host of the SRT stream."""

    port: int = Field(10000, ge=1, le=65535)
    """Port of the SRT stream."""

    @property
    def url(self) -> str:
        """URL of the SRT stream."""

        host = gethostbyname(self.host)
        port = self.port
        return f"srt://{host}:{port}"


class EmistreamConfig(BaseModel):
    """Configuration for the emistream service."""

    http: EmistreamHTTPConfig = EmistreamHTTPConfig()
    """Configuration for the HTTP API."""

    srt: EmistreamSRTConfig = EmistreamSRTConfig()
    """Configuration for the SRT stream."""


class Config(BaseConfig):
    """Configuration for the service."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    store: StoreConfig = StoreConfig()
    """Configuration for the store."""

    operations: OperationsConfig = OperationsConfig()
    """Configuration for the operations."""

    cleaner: CleanerConfig = CleanerConfig()
    """Configuration for the cleaner."""

    synchronizer: SynchronizerConfig = SynchronizerConfig()
    """Configuration for the synchronizer."""

    emilounge: EmiloungeConfig = EmiloungeConfig()
    """Configuration for the emilounge service."""

    emirecords: EmirecordsConfig = EmirecordsConfig()
    """Configuration for the emirecords service."""

    emishows: EmishowsConfig = EmishowsConfig()
    """Configuration for the emishows service."""

    emistream: EmistreamConfig = EmistreamConfig()
    """Configuration for the emistream service."""

    debug: bool = False
    """Enable debug mode."""

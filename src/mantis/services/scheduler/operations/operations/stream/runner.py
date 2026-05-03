from collections.abc import Mapping, Sequence
from math import ceil
from pathlib import Path

from pystreams.base import Stream
from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata

from mantis.config.models import Config
from mantis.services.octopus import models as om


class Runner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _map_format(self, fmt: om.Format) -> str:
        match fmt:
            case om.Format.OGG:
                return "ogg"

    def _build_stream_input(self, path: Path, fmt: om.Format) -> FFmpegNode:
        return FFmpegNode(
            target=str(path),
            options={"f": self._map_format(fmt), "re": True},
        )

    def _build_ffmpeg_metadata_options(
        self, metadata: Mapping[str, str] | None
    ) -> Sequence[str]:
        return [f"{key}={value}" for key, value in (metadata or {}).items()]

    def _build_stream_output(
        self,
        fmt: om.Format,
        credentials: om.Credentials,
        metadata: Mapping[str, str] | None,
    ) -> FFmpegNode:
        latency = ceil(self._config.operations.stream.latency.total_seconds() * 1000000)

        return FFmpegNode(
            target=self._config.octopus.srt.url,
            options={
                "acodec": "copy",
                "f": self._map_format(fmt),
                "latency": latency,
                "map": "0:a",
                "metadata": self._build_ffmpeg_metadata_options(metadata),
                "mode": "caller",
                "passphrase": credentials.token,
            },
        )

    def _build_stream_metadata(
        self,
        path: Path,
        fmt: om.Format,
        credentials: om.Credentials,
        metadata: Mapping[str, str] | None,
    ) -> FFmpegStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_stream_input(path, fmt),
            output=self._build_stream_output(fmt, credentials, metadata),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self,
        path: Path,
        fmt: om.Format,
        credentials: om.Credentials,
        metadata: Mapping[str, str] | None,
    ) -> Stream:
        """Run the stream."""
        meta = self._build_stream_metadata(path, fmt, credentials, metadata)
        return await self._run_stream(meta)

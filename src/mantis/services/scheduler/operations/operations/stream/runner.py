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
            options={
                "f": self._map_format(fmt),
                "re": True,
            },
        )

    def _build_stream_output(
        self, fmt: om.Format, credentials: om.Credentials
    ) -> FFmpegNode:
        return FFmpegNode(
            target=self._config.octopus.srt.url,
            options={
                "acodec": "copy",
                "f": self._map_format(fmt),
                "passphrase": credentials.token,
            },
        )

    def _build_stream_metadata(
        self, path: Path, fmt: om.Format, credentials: om.Credentials
    ) -> FFmpegStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_stream_input(path, fmt),
            output=self._build_stream_output(fmt, credentials),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self, path: Path, fmt: om.Format, credentials: om.Credentials
    ) -> Stream:
        """Run the stream."""
        metadata = self._build_stream_metadata(path, fmt, credentials)
        return await self._run_stream(metadata)

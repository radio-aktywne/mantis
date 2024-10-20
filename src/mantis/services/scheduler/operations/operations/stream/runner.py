from pathlib import Path

from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata
from pystreams.stream import Stream

from mantis.config.models import Config
from mantis.services.octopus import models as om


class Runner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def _map_format(self, format: om.Format) -> str:
        match format:
            case om.Format.OGG:
                return "ogg"

    def _build_stream_input(self, path: Path, format: om.Format) -> FFmpegNode:
        return FFmpegNode(
            target=str(path),
            options={
                "f": self._map_format(format),
                "re": True,
            },
        )

    def _build_stream_output(
        self, format: om.Format, credentials: om.Credentials
    ) -> FFmpegNode:
        return FFmpegNode(
            target=self._config.octopus.srt.url,
            options={
                "acodec": "copy",
                "f": self._map_format(format),
                "passphrase": credentials.token,
            },
        )

    def _build_stream_metadata(
        self, path: Path, format: om.Format, credentials: om.Credentials
    ) -> FFmpegStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_stream_input(path, format),
            output=self._build_stream_output(format, credentials),
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        return await ProcessBasedStreamFactory().create(metadata)

    async def run(
        self, path: Path, format: om.Format, credentials: om.Credentials
    ) -> Stream:
        """Run the stream."""

        metadata = self._build_stream_metadata(path, format, credentials)
        return await self._run_stream(metadata)

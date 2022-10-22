from datetime import timedelta

from rocketry import Rocketry

from emischeduler.archive.client import ArchiveClient
from emischeduler.config import Config
from emischeduler.scheduler.log import setup_logger
from emischeduler.scheduler.tasks.sync import sync
from emischeduler.shows.client import ShowsClient
from emischeduler.stream.client import StreamClient


def build(config: Config) -> Rocketry:
    app = Rocketry(
        config={
            "task_execution": "async",
            "instant_shutdown": True,
        },
        parameters={
            "config": config,
            "stream": StreamClient(
                host=config.emistream.host,
                port=config.emistream.port,
                http_kwargs={"follow_redirects": True},
            ),
            "shows": ShowsClient(
                host=config.emishows.host,
                port=config.emishows.port,
                http_kwargs={"follow_redirects": True},
            ),
            "archive": ArchiveClient(
                endpoint=f"{config.emiarchive.host}:{config.emiarchive.port}",
                access_key=config.emiarchive.username,
                secret_key=config.emiarchive.password,
                secure=config.emiarchive.secure,
            ),
            "groups": {},
        },
    )

    setup_logger(config)

    app.task(
        name="sync",
        func=sync,
        start_cond="minutely",
        parameters={"delta": timedelta(days=1)},
    )

    return app

"""Main script.

This module provides basic CLI entrypoint.

"""
import logging
import sys
from datetime import time
from typing import List, Optional

import typer
from redis.exceptions import RedisError
from rq import Connection
from rq.registry import ScheduledJobRegistry
from typer import FileText

from emischeduler import log
from emischeduler.config.models import Config
from emischeduler.config.utils import get_config
from emischeduler.dashboard import Dashboard
from emischeduler.jobs.sync import enqueue_sync_at
from emischeduler.queues import QueueRegistry
from emischeduler.redis import get_redis_client
from emischeduler.utils import next_at, GracefulShutdown
from emischeduler.workers import WorkerPoolRegistry

cli = typer.Typer()  # this is actually callable and thus can be an entry point

logger = logging.getLogger(__name__)


def enqueue_sync(config: Config, queues: QueueRegistry) -> None:
    if ScheduledJobRegistry(queue=queues.sync_queue).count == 0:
        enqueue_sync_at(config, queues.keys(), next_at(time(hour=3)))


@cli.command()
def main(
    config_file: Optional[FileText] = typer.Option(
        None, "--config-file", "-C", dir_okay=False, help="Configuration file."
    ),
    config: Optional[List[str]] = typer.Option(
        None, "--config", "-c", help="Configuration entries."
    ),
    verbosity: log.Verbosity = typer.Option(
        "INFO", "--verbosity", "-v", help="Verbosity level."
    ),
) -> None:
    """Command line interface for emischeduler."""

    log.configure(verbosity)

    logger.info("Loading config...")
    try:
        config = get_config(config_file, config)
    except ValueError as e:
        logger.error("Failed to parse config!", exc_info=e)
        raise typer.Exit(1)
    logger.info("Config loaded!")

    try:
        client = get_redis_client(config.redis)
        client.ping()
    except (ConnectionError, RedisError) as e:
        logger.error("Can't connect to redis.", exc_info=e)
        sys.exit(1)

    with Connection(client):
        dashboard = Dashboard(config)
        queues = QueueRegistry()
        pools = WorkerPoolRegistry(queues)
        pools.start()
        dashboard.start()
        enqueue_sync(config, queues)
        with GracefulShutdown():
            pools.wait()
            dashboard.wait()


if __name__ == "__main__":
    # entry point for "python -m"
    cli()

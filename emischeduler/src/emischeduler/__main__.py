"""Main script.

This module provides basic CLI entrypoint.

"""

import logging
import sys
from datetime import time

import typer
from redis import RedisError
from rq import Connection
from rq.registry import ScheduledJobRegistry

from emischeduler.dashboard import Dashboard
from emischeduler.jobs.sync import enqueue_sync_at
from emischeduler.queues import QueueRegistry
from emischeduler.redis import get_redis_client
from emischeduler.utils import GracefulShutdown, next_at
from emischeduler.workers import WorkerPoolRegistry

cli = typer.Typer()  # this is actually callable and thus can be an entry point


def config_logging() -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def enqueue_sync(queues: QueueRegistry) -> None:
    if ScheduledJobRegistry(queue=queues.sync_queue).count == 0:
        enqueue_sync_at(queues.keys(), next_at(time(hour=3)))


@cli.command()
def main():
    """Command line interface for emischeduler."""

    config_logging()

    try:
        client = get_redis_client()
        client.ping()
    except (ConnectionError, RedisError) as e:
        logging.error("Can't connect to redis.", exc_info=e)
        sys.exit(1)

    with Connection(client):
        dashboard = Dashboard()
        queues = QueueRegistry()
        pools = WorkerPoolRegistry(queues)
        pools.start()
        dashboard.start()
        enqueue_sync(queues)
        with GracefulShutdown():
            pools.wait()
            dashboard.wait()


if __name__ == "__main__":
    # entry point for "python -m"
    cli()

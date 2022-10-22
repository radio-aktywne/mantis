"""Main script.

This module provides basic CLI entrypoint.

"""
import logging
from typing import List, Optional

import typer
from typer import FileText

from emischeduler import log
from emischeduler.api.app import build as build_api
from emischeduler.config import get_config
from emischeduler.scheduler.app import build as build_scheduler
from emischeduler.server import run

cli = typer.Typer()  # this is actually callable and thus can be an entry point

logger = logging.getLogger(__name__)


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

    scheduler = build_scheduler(config)
    api = build_api(config, scheduler)

    run(scheduler, api, config)


if __name__ == "__main__":
    # entry point for "python -m"
    cli()

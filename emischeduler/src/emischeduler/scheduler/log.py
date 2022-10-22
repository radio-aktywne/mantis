import logging

from redbird.logging import RepoHandler
from redbird.repos import CSVFileRepo
from rocketry.log import MinimalRecord

from emischeduler.config import Config


def setup_logger(config: Config) -> None:
    repo = CSVFileRepo(filename=config.log_file, model=MinimalRecord)
    logger = logging.getLogger("rocketry.task")
    handler = RepoHandler(repo=repo)
    logger.addHandler(handler)

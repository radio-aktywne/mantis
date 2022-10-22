import logging
from pathlib import Path
from typing import Dict
from uuid import UUID

from rocketry.args import Arg

from emischeduler.models.data import TaskGroup

logger = logging.getLogger(__name__)


async def cleanup(
    path: str | Path,
    group: UUID,
    groups: Dict[UUID, TaskGroup] = Arg("groups"),
) -> None:
    path = Path(path)
    logger.info("Cleaning up ...")

    logger.info(f"Cleaning up {path}...")
    Path.unlink(path, missing_ok=True)
    logger.info(f"Cleaned up {path}.")

    logger.info(f"Removing {group} from groups...")
    groups.pop(group, None)
    logger.info(f"Removed {group} from groups.")

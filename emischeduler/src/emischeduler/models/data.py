from dataclasses import dataclass
from typing import List

from rocketry.core import Task

from emischeduler.shows.models.data import Event


@dataclass
class TaskGroup:
    event: Event
    tasks: List[Task]

import json
from datetime import datetime
from typing import Optional

from rocketry.core import Task as RocketryTask

from emischeduler.models.base import SerializableModel


class Task(SerializableModel):
    name: str
    description: Optional[str]
    priority: int
    start_cond: Optional[str]
    end_cond: Optional[str]
    timeout: Optional[int]
    disabled: bool
    force_termination: bool
    force_run: bool
    status: Optional[str]
    is_running: bool
    last_run: Optional[datetime]
    last_success: Optional[datetime]
    last_fail: Optional[datetime]
    last_terminate: Optional[datetime]
    last_inaction: Optional[datetime]
    last_crash: Optional[datetime]

    @staticmethod
    def from_task(task: RocketryTask) -> "Task":
        try:
            start_cond = str(task.start_cond)
        except Exception:
            start_cond = None

        try:
            end_cond = str(task.end_cond)
        except Exception:
            end_cond = None

        return Task(
            start_cond=start_cond,
            end_cond=end_cond,
            is_running=task.is_running,
            **json.loads(task.json(exclude={"start_cond", "end_cond"})),
        )

import re
from datetime import datetime

from rocketry.args import Task as TaskArg
from rocketry.core import Task, BaseCondition

from emischeduler.time import (
    utcnow,
    to_utc,
    stringify,
    parse_datetime_with_timezone,
)


class At(BaseCondition):
    __parsers__ = {re.compile(r"once at (?P<outcome>.+)"): "__init__"}

    def __init__(self, dt: str | datetime) -> None:
        super().__init__()
        dt = parse_datetime_with_timezone(dt) if isinstance(dt, str) else dt
        self._dt = to_utc(dt)
        self._str = f"once at {stringify(self._dt)}"

    def get_state(self, task: Task = TaskArg()) -> bool:
        return task.last_run is None and utcnow() >= self._dt


at = At

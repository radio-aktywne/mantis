from typing import List

from emischeduler.api.models import Task
from emischeduler.models.base import SerializableModel


class TasksResponse(SerializableModel):
    tasks: List[Task]


class TaskResponse(SerializableModel):
    task: Task


class DisableTaskResponse(SerializableModel):
    task: Task


class EnableTaskResponse(SerializableModel):
    task: Task


class TerminateTaskResponse(SerializableModel):
    task: Task


class RunTaskResponse(SerializableModel):
    task: Task

from rocketry import Rocketry
from rocketry.core import Task as RocketryTask
from starlite import Controller, State, get, post

from emischeduler.api.models import Task
from emischeduler.api.paths.tasks.models import TasksResponse, TaskResponse


class TasksController(Controller):
    path = None

    @get()
    async def tasks(self, state: State) -> TasksResponse:
        scheduler: Rocketry = state.scheduler
        tasks = [Task.from_task(task) for task in scheduler.session.tasks]
        return TasksResponse(tasks=tasks)

    @get("/{task_name:str}")
    async def task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        task: RocketryTask = scheduler.session[task_name]
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/disable")
    async def disable_task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        task: RocketryTask = scheduler.session[task_name]
        task.disabled = True
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/enable")
    async def enable_task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        task: RocketryTask = scheduler.session[task_name]
        task.disabled = False
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/terminate")
    async def terminate_task(
        self, state: State, task_name: str
    ) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        task: RocketryTask = scheduler.session[task_name]
        task.force_termination = True
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/run")
    async def run_task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        task: RocketryTask = scheduler.session[task_name]
        task.force_run = True
        return TaskResponse(task=Task.from_task(task))

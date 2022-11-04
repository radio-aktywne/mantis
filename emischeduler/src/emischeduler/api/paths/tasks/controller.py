from rocketry import Rocketry
from rocketry.core import Task as RocketryTask
from starlite import Controller, State, get, post, NotFoundException

from emischeduler.api.models import Task
from emischeduler.api.paths.tasks.models import TasksResponse, TaskResponse


class TasksController(Controller):
    path = None

    @get()
    async def tasks(self, state: State) -> TasksResponse:
        scheduler: Rocketry = state.scheduler
        tasks = [Task.from_task(task) for task in scheduler.session.tasks]
        return TasksResponse(tasks=tasks)

    @get("/{task_name:str}", raises=[NotFoundException])
    async def task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        if task_name not in scheduler.session:
            raise NotFoundException(f"Task {task_name} not found.")
        task: RocketryTask = scheduler.session[task_name]
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/disable", raises=[NotFoundException])
    async def disable_task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        if task_name not in scheduler.session:
            raise NotFoundException(f"Task {task_name} not found.")
        task: RocketryTask = scheduler.session[task_name]
        task.disabled = True
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/enable", raises=[NotFoundException])
    async def enable_task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        if task_name not in scheduler.session:
            raise NotFoundException(f"Task {task_name} not found.")
        task: RocketryTask = scheduler.session[task_name]
        task.disabled = False
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/terminate", raises=[NotFoundException])
    async def terminate_task(
        self, state: State, task_name: str
    ) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        if task_name not in scheduler.session:
            raise NotFoundException(f"Task {task_name} not found.")
        task: RocketryTask = scheduler.session[task_name]
        task.force_termination = True
        return TaskResponse(task=Task.from_task(task))

    @post("/{task_name:str}/run", raises=[NotFoundException])
    async def run_task(self, state: State, task_name: str) -> TaskResponse:
        scheduler: Rocketry = state.scheduler
        if task_name not in scheduler.session:
            raise NotFoundException(f"Task {task_name} not found.")
        task: RocketryTask = scheduler.session[task_name]
        task.force_run = True
        return TaskResponse(task=Task.from_task(task))

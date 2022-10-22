from starlite import Router

from emischeduler.api.paths.tasks.controller import TasksController

router = Router(path="/tasks", route_handlers=[TasksController])

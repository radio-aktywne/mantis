from starlite import Router

from emischeduler.api.paths.status.router import router as status_router
from emischeduler.api.paths.tasks.router import router as tasks_router

router = Router(path="/", route_handlers=[status_router, tasks_router])

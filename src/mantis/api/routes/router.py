from litestar import Router

from mantis.api.routes.ping.router import router as ping_router
from mantis.api.routes.tasks.router import router as tasks_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        tasks_router,
    ],
)

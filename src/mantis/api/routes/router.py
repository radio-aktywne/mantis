from litestar import Router

from mantis.api.routes.ping.router import router as ping_router
from mantis.api.routes.sse.router import router as sse_router
from mantis.api.routes.tasks.router import router as tasks_router
from mantis.api.routes.test.router import router as test_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        sse_router,
        tasks_router,
        test_router,
    ],
)

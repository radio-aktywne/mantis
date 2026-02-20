from litestar import Router

from mantis.api.routes.ping.router import router as ping
from mantis.api.routes.sse.router import router as sse
from mantis.api.routes.tasks.router import router as tasks
from mantis.api.routes.test.router import router as test

router = Router(
    path="/",
    route_handlers=[
        ping,
        sse,
        tasks,
        test,
    ],
)

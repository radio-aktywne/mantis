from litestar import Router

from emischeduler.api.routes.tasks.controller import Controller

router = Router(
    path="/tasks",
    route_handlers=[
        Controller,
    ],
)

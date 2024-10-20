from litestar import Router

from mantis.api.routes.tasks.controller import Controller

router = Router(
    path="/tasks",
    route_handlers=[
        Controller,
    ],
)

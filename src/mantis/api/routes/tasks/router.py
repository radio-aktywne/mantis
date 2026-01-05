from litestar import Router

from mantis.api.routes.tasks.controller import Controller

router = Router(
    path="/tasks",
    tags=["Tasks"],
    route_handlers=[
        Controller,
    ],
)

from starlite import Router

from emischeduler.api.paths.status.controller import StatusController

router = Router(path="/status", route_handlers=[StatusController])

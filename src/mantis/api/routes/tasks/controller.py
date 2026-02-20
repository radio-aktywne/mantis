from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.di import Provide
from litestar.params import Body, Parameter
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK

from mantis.api.exceptions import BadRequestException, NotFoundException
from mantis.api.routes.tasks import errors as e
from mantis.api.routes.tasks import models as m
from mantis.api.routes.tasks.service import Service
from mantis.models.base import Serializable
from mantis.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(scheduler=state.scheduler)

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the tasks endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="Get index",
    )
    async def list(
        self, service: Service
    ) -> Response[Serializable[m.ListResponseTasks]]:
        """List tasks."""
        request = m.ListRequest()

        response = await service.list(request)

        return Response(Serializable(response.tasks))

    @handlers.get(
        "/{id:str}",
        summary="Get task",
        raises=[NotFoundException],
    )
    async def get(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.GetRequestId],
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[Serializable[m.GetResponseTask]]:
        """Get a task."""
        request = m.GetRequest(id=id.root)

        try:
            response = await service.get(request)
        except e.TaskNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.task))

    @handlers.get(
        "/pending/{id:str}",
        summary="Get pending task",
        raises=[NotFoundException],
    )
    async def get_pending(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.GetPendingRequestId],
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[Serializable[m.GetPendingResponseTask]]:
        """Get a pending task."""
        request = m.GetPendingRequest(id=id.root)

        try:
            response = await service.get_pending(request)
        except e.TaskNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.task))

    @handlers.get(
        "/running/{id:str}",
        summary="Get running task",
        raises=[NotFoundException],
    )
    async def get_running(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.GetRunningRequestId],
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[Serializable[m.GetRunningResponseTask]]:
        """Get a running task."""
        request = m.GetRunningRequest(id=id.root)

        try:
            response = await service.get_running(request)
        except e.TaskNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.task))

    @handlers.get(
        "/cancelled/{id:str}",
        summary="Get cancelled task",
        raises=[NotFoundException],
    )
    async def get_cancelled(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.GetCancelledRequestId],
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[Serializable[m.GetCancelledResponseTask]]:
        """Get a cancelled task."""
        request = m.GetCancelledRequest(id=id.root)

        try:
            response = await service.get_cancelled(request)
        except e.TaskNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.task))

    @handlers.get(
        "/failed/{id:str}",
        summary="Get failed task",
        raises=[NotFoundException],
    )
    async def get_failed(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.GetFailedRequestId],
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[Serializable[m.GetFailedResponseTask]]:
        """Get a failed task."""
        request = m.GetFailedRequest(id=id.root)

        try:
            response = await service.get_failed(request)
        except e.TaskNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.task))

    @handlers.get(
        "/completed/{id:str}",
        summary="Get completed task",
        raises=[NotFoundException],
    )
    async def get_completed(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.GetCompletedRequestId],
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[Serializable[m.GetCompletedResponseTask]]:
        """Get a completed task."""
        request = m.GetCompletedRequest(id=id.root)

        try:
            response = await service.get_completed(request)
        except e.TaskNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.task))

    @handlers.post(
        summary="Schedule task",
        raises=[BadRequestException],
    )
    async def schedule(
        self,
        service: Service,
        data: Annotated[
            Serializable[m.ScheduleRequestData],
            Body(
                description="Data to schedule a task.",
            ),
        ],
    ) -> Response[Serializable[m.ScheduleResponseTask]]:
        """Schedule a task."""
        request = m.ScheduleRequest(data=data.root)

        try:
            response = await service.schedule(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.task))

    @handlers.delete(
        "/{id:str}",
        summary="Cancel task",
        status_code=HTTP_200_OK,
        raises=[NotFoundException],
    )
    async def cancel(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.CancelRequestId],
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[Serializable[m.CancelResponseTask]]:
        """Cancel a task."""
        request = m.CancelRequest(id=id.root)

        try:
            response = await service.cancel(request)
        except e.TaskNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.task))

    @handlers.post(
        "/clean",
        summary="Clean tasks",
        status_code=HTTP_200_OK,
        raises=[BadRequestException],
    )
    async def clean(
        self,
        service: Service,
        data: Annotated[
            Serializable[m.CleanRequestData],
            Body(
                description="Data to clean tasks.",
            ),
        ],
    ) -> Response[Serializable[m.CleanResponseResults]]:
        """Clean tasks."""
        request = m.CleanRequest(data=data.root)

        try:
            response = await service.clean(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.results))

from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.di import Provide
from litestar.params import Body, Parameter
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK

from emischeduler.api.exceptions import BadRequestException, NotFoundException
from emischeduler.api.routes.tasks import errors as e
from emischeduler.api.routes.tasks import models as m
from emischeduler.api.routes.tasks.service import Service
from emischeduler.api.validator import Validator
from emischeduler.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            scheduler=state.scheduler,
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the tasks endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="Get index",
    )
    async def list(self, service: Service) -> Response[m.ListResponseTasks]:
        """List tasks."""

        req = m.ListRequest()

        req = await service.list(req)

        tasks = req.tasks

        return Response(tasks)

    @handlers.get(
        "/{id:uuid}",
        summary="Get task",
        raises=[
            NotFoundException,
        ],
    )
    async def get(
        self,
        service: Service,
        id: Annotated[
            m.GetRequestId,
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[m.GetResponseTask]:
        """Get a task."""

        req = m.GetRequest(
            id=id,
        )

        try:
            res = await service.get(req)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.get(
        "/pending/{id:uuid}",
        summary="Get pending task",
        raises=[
            NotFoundException,
        ],
    )
    async def get_pending(
        self,
        service: Service,
        id: Annotated[
            m.GetPendingRequestId,
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[m.GetPendingResponseTask]:
        """Get a pending task."""

        req = m.GetPendingRequest(
            id=id,
        )

        try:
            res = await service.get_pending(req)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.get(
        "/running/{id:uuid}",
        summary="Get running task",
        raises=[
            NotFoundException,
        ],
    )
    async def get_running(
        self,
        service: Service,
        id: Annotated[
            m.GetRunningRequestId,
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[m.GetRunningResponseTask]:
        """Get a running task."""

        req = m.GetRunningRequest(
            id=id,
        )

        try:
            res = await service.get_running(req)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.get(
        "/cancelled/{id:uuid}",
        summary="Get cancelled task",
        raises=[
            NotFoundException,
        ],
    )
    async def get_cancelled(
        self,
        service: Service,
        id: Annotated[
            m.GetCancelledRequestId,
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[m.GetCancelledResponseTask]:
        """Get a cancelled task."""

        req = m.GetCancelledRequest(
            id=id,
        )

        try:
            res = await service.get_cancelled(req)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.get(
        "/failed/{id:uuid}",
        summary="Get failed task",
        raises=[
            NotFoundException,
        ],
    )
    async def get_failed(
        self,
        service: Service,
        id: Annotated[
            m.GetFailedRequestId,
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[m.GetFailedResponseTask]:
        """Get a failed task."""

        req = m.GetFailedRequest(
            id=id,
        )

        try:
            res = await service.get_failed(req)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.get(
        "/completed/{id:uuid}",
        summary="Get completed task",
        raises=[
            NotFoundException,
        ],
    )
    async def get_completed(
        self,
        service: Service,
        id: Annotated[
            m.GetCompletedRequestId,
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[m.GetCompletedResponseTask]:
        """Get a completed task."""

        req = m.GetCompletedRequest(
            id=id,
        )

        try:
            res = await service.get_completed(req)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.post(
        summary="Schedule task",
        raises=[
            BadRequestException,
        ],
    )
    async def schedule(
        self,
        service: Service,
        data: Annotated[
            m.ScheduleRequestData,
            Body(
                description="Data to schedule a task.",
            ),
        ],
    ) -> Response[m.ScheduleResponseTask]:
        """Schedule a task."""

        data = Validator(m.ScheduleRequestData).object(data)

        req = m.ScheduleRequest(
            data=data,
        )

        try:
            res = await service.schedule(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.delete(
        "/{id:uuid}",
        summary="Cancel task",
        status_code=HTTP_200_OK,
        raises=[
            NotFoundException,
        ],
    )
    async def cancel(
        self,
        service: Service,
        id: Annotated[
            m.CancelRequestId,
            Parameter(
                description="Identifier of the task.",
            ),
        ],
    ) -> Response[m.CancelResponseTask]:
        """Cancel a task."""

        req = m.CancelRequest(
            id=id,
        )

        try:
            res = await service.cancel(req)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        task = res.task

        return Response(task)

    @handlers.post(
        "/clean",
        summary="Clean tasks",
        status_code=HTTP_200_OK,
        raises=[
            BadRequestException,
        ],
    )
    async def clean(
        self,
        service: Service,
        data: Annotated[
            m.CleanRequestData,
            Body(
                description="Data to clean tasks.",
            ),
        ],
    ) -> Response[m.CleanResponseResults]:
        """Clean tasks."""

        data = Validator(m.CleanRequestData).object(data)

        req = m.CleanRequest(
            data=data,
        )

        try:
            res = await service.clean(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex

        results = res.results

        return Response(results)

from litestar import Controller as BaseController
from litestar import delete, get, post
from litestar.di import Provide
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK

from emischeduler.api.exceptions import NotFoundException, UnprocessableContentException
from emischeduler.api.routes.tasks import errors as e
from emischeduler.api.routes.tasks import models as m
from emischeduler.api.routes.tasks.service import Service
from emischeduler.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(scheduler=state.scheduler)

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the tasks endpoint."""

    dependencies = DependenciesBuilder().build()

    @get(
        summary="Get index",
        description="Get tasks index.",
    )
    async def get_index(self, service: Service) -> Response[m.GetIndexResponse]:
        response = await service.get_index()
        return Response(response)

    @get(
        "/{id:uuid}",
        summary="Get task",
        description="Get task by id.",
        raises=[NotFoundException],
    )
    async def get_task(
        self, service: Service, id: m.GetTaskIdParameter
    ) -> Response[m.GetTaskResponse]:
        try:
            response = await service.get_task(id)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=id) from ex

        return Response(response)

    @get(
        "/pending/{id:uuid}",
        summary="Get pending task",
        description="Get pending task by id.",
        raises=[NotFoundException],
    )
    async def get_pending_task(
        self, service: Service, id: m.GetPendingTaskIdParameter
    ) -> Response[m.GetPendingTaskResponse]:
        try:
            response = await service.get_pending_task(id)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=id) from ex

        return Response(response)

    @get(
        "/running/{id:uuid}",
        summary="Get running task",
        description="Get running task by id.",
        raises=[NotFoundException],
    )
    async def get_running_task(
        self, service: Service, id: m.GetRunningTaskIdParameter
    ) -> Response[m.GetRunningTaskResponse]:
        try:
            response = await service.get_running_task(id)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=id) from ex

        return Response(response)

    @get(
        "/cancelled/{id:uuid}",
        summary="Get cancelled task",
        description="Get cancelled task by id.",
        raises=[NotFoundException],
    )
    async def get_cancelled_task(
        self, service: Service, id: m.GetCancelledTaskIdParameter
    ) -> Response[m.GetCancelledTaskResponse]:
        try:
            response = await service.get_cancelled_task(id)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=id) from ex

        return Response(response)

    @get(
        "/failed/{id:uuid}",
        summary="Get failed task",
        description="Get failed task by id.",
        raises=[NotFoundException],
    )
    async def get_failed_task(
        self, service: Service, id: m.GetFailedTaskIdParameter
    ) -> Response[m.GetFailedTaskResponse]:
        try:
            response = await service.get_failed_task(id)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=id) from ex

        return Response(response)

    @get(
        "/completed/{id:uuid}",
        summary="Get completed task",
        description="Get completed task by id.",
        raises=[NotFoundException],
    )
    async def get_completed_task(
        self, service: Service, id: m.GetCompletedTaskIdParameter
    ) -> Response[m.GetCompletedTaskResponse]:
        try:
            response = await service.get_completed_task(id)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=id) from ex

        return Response(response)

    @post(
        summary="Schedule task",
        description="Schedule a task.",
        raises=[UnprocessableContentException],
    )
    async def schedule_task(
        self, service: Service, data: m.ScheduleTaskRequest
    ) -> Response[m.ScheduleTaskResponse]:
        try:
            response = await service.schedule_task(data)
        except e.InvalidRequestError as ex:
            raise UnprocessableContentException(extra=ex.message) from ex
        return Response(response)

    @delete(
        "/{id:uuid}",
        summary="Cancel task",
        description="Cancel a task.",
        raises=[NotFoundException],
        status_code=HTTP_200_OK,
    )
    async def cancel_task(
        self, service: Service, id: m.CancelTaskIdParameter
    ) -> Response[m.CancelTaskResponse]:
        try:
            response = await service.cancel_task(id)
        except e.TaskNotFoundError as ex:
            raise NotFoundException(extra=id) from ex

        return Response(response)

    @post(
        "/clean",
        summary="Clean tasks",
        description="Clean stale tasks.",
        raises=[UnprocessableContentException],
        status_code=HTTP_200_OK,
    )
    async def clean_tasks(
        self, service: Service, data: m.CleanTasksRequest
    ) -> Response[m.CleanTasksResponse]:
        try:
            response = await service.clean_tasks(data)
        except e.InvalidRequestError as ex:
            raise UnprocessableContentException(extra=ex.message) from ex

        return Response(response)

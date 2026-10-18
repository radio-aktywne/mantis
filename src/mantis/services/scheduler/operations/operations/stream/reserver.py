import asyncio

from mantis.config.models import Config
from mantis.services.apis.octopus import errors as oe, models as om
from mantis.services.apis.octopus.service import OctopusService
from mantis.services.scheduler.operations.operations.stream import (
    errors as e,
    models as m,
)
from mantis.utils.time import awareutcnow


class Reserver:
    """Utility to reserve a stream."""

    def __init__(self, config: Config, octopus: OctopusService) -> None:
        self._config = config
        self._octopus = octopus

    async def _subscribe_to_availability_changes(self) -> om.SubscribeResponseMessages:
        subscribe_request = om.SubscribeRequest(
            types={om.EventType.AVAILABILITY_CHANGED}
        )

        subscribe_response = await self._octopus.subscribe(subscribe_request)

        return subscribe_response.messages

    async def _try_reserve(
        self, request: m.ReserveRequest
    ) -> om.ReserveResponseReservation | None:
        try:
            reserve_request = om.ReserveRequest(
                data=om.ReservationInput(
                    instance=om.Instance(
                        event=request.instance.event.id, start=request.instance.start
                    ),
                    format=request.format,
                )
            )
            reserve_response = await self._octopus.reserve(reserve_request)
        except oe.ConflictError:
            return None
        else:
            return reserve_response.reservation

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        changes = await self._subscribe_to_availability_changes()

        try:
            deadline = awareutcnow() + self._config.operations.stream.timeout

            while awareutcnow() < deadline:
                change = asyncio.ensure_future(anext(changes))

                try:
                    reservation = await self._try_reserve(request)

                    if reservation is not None:
                        return m.ReserveResponse(credentials=reservation.credentials)

                    timeout = (deadline - awareutcnow()).total_seconds()
                    await asyncio.wait_for(change, timeout=timeout)
                finally:
                    change.cancel()
                    await asyncio.wait([change])

            raise e.ReservationFailedError(request.instance)
        finally:
            await changes.aclose()

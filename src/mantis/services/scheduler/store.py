import json
from types import TracebackType
from typing import override

from pyscheduler.models.data import runtime as r
from pyscheduler.models.data import storage as s
from pyscheduler.protocols import store as st
from pystores import file as f

from mantis.config.models import StoreConfig


class Serializer(f.Serializer[s.State, str]):
    """Serializer for state to JSON string."""

    @override
    async def serialize(self, value: s.State) -> str:
        return json.dumps(value, separators=(",", ":"))

    @override
    async def deserialize(self, value: str) -> s.State:
        return json.loads(value)


class Store(f.FileStore[s.State, str], st.Store[s.State]):
    """Store for scheduler state."""

    def __init__(self, config: StoreConfig) -> None:
        path = config.path

        if not path.exists():
            path.touch()

        super().__init__(
            file=path.open("r+"),
            serializer=Serializer(),
            default=self._build_default_state(),
        )

    async def __aenter__(self) -> "Store":
        return self

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._file.close()

    def _build_default_state(self) -> s.State:
        state = r.State(
            tasks=r.Tasks(
                pending={},
                running={},
                cancelled={},
                failed={},
                completed={},
            ),
            statuses={},
            relationships=r.Relationships(
                dependents={},
                dependencies={},
            ),
        )

        return state.serialize()

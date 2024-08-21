import json

from pyscheduler.models.data import runtime as r
from pyscheduler.models.data import storage as s
from pyscheduler.protocols import store as st
from pystores import file as f

from emischeduler.config.models import StoreConfig


class Serializer(f.Serializer[s.State, str]):
    async def serialize(self, state: s.State) -> str:
        return json.dumps(state, separators=(",", ":"))

    async def deserialize(self, state: str) -> s.State:
        return json.loads(state)


class Store(f.FileStore[s.State, str], st.Store[s.State]):
    def __init__(self, config: StoreConfig) -> None:
        path = config.path

        if not path.exists():
            path.touch()

        super().__init__(
            file=open(path, "r+t"),
            serializer=Serializer(),
            default=self._build_default_state(),
        )

    async def __aenter__(self) -> "Store":
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
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

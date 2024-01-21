from pyscheduler.models.data import runtime as r
from pyscheduler.models.data import storage as s
from pyscheduler.protocols import store as st
from pystores.memory import MemoryStore


class Store(MemoryStore[s.State], st.Store[s.State]):
    def __init__(self) -> None:
        super().__init__(self._build_initial_state())

    def _build_initial_state(self) -> s.State:
        state = r.State(
            tasks=r.Tasks(
                pending={}, running={}, cancelled={}, failed={}, completed={}
            ),
            statuses={},
            relationships=r.Relationships(dependents={}, dependencies={}),
        )
        return state.serialize()

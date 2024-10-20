import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import pytest_asyncio
from httpx import AsyncClient, BasicAuth
from litestar import Litestar
from litestar.testing import AsyncTestClient

from mantis.api.app import AppBuilder
from mantis.config.builder import ConfigBuilder
from mantis.config.models import Config
from tests.utils.containers import AsyncDockerContainer
from tests.utils.waiting.conditions import CallableCondition, CommandCondition
from tests.utils.waiting.strategies import TimeoutStrategy
from tests.utils.waiting.waiter import Waiter


@pytest.fixture(scope="session")
def path() -> Generator[Path]:
    """Path to the store file."""

    with TemporaryDirectory() as directory:
        yield Path(directory) / "state.json"


@pytest.fixture(scope="session")
def env(path: Path) -> Generator[dict[str, str]]:
    """Environment variables."""

    old = os.environ.copy()

    try:
        os.environ["MANTIS__STORE__PATH"] = str(path)

        yield os.environ
    finally:
        os.environ.clear()
        os.environ.update(old)


@pytest.fixture(scope="session")
def config(env: dict[str, str]) -> Config:
    """Loaded configuration."""

    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Reusable application."""

    return AppBuilder(config).build()


@pytest_asyncio.fixture(scope="session")
async def quokka() -> AsyncGenerator[AsyncDockerContainer]:
    """Quokka container."""

    async def _check() -> None:
        auth = BasicAuth(username="admin", password="password")
        async with AsyncClient(base_url="http://localhost:10000", auth=auth) as client:
            response = await client.get("/admin/stats.json")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/services/quokka:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def dingo(
    quokka: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer]:
    """Dingo container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/services/dingo:latest",
        network="host",
    )

    async with container as container:
        await asyncio.sleep(5)
        yield container


@pytest_asyncio.fixture(scope="session")
async def amber() -> AsyncGenerator[AsyncDockerContainer]:
    """Amber container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10610") as client:
            response = await client.get("/minio/health/ready")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/amber:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def numbat(
    amber: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer]:
    """Numbat container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10600") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/services/numbat:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def emerald() -> AsyncGenerator[AsyncDockerContainer]:
    """Emerald container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10710") as client:
            response = await client.get("/minio/health/ready")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/emerald:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def gecko(
    emerald: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer]:
    """Gecko container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10700") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/services/gecko:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def octopus(
    dingo: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer]:
    """Octopus container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10300") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/services/octopus:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def sapphire() -> AsyncGenerator[AsyncDockerContainer]:
    """Sapphire container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/sapphire:latest",
        network="host",
        privileged=True,
    )

    waiter = Waiter(
        condition=CommandCondition(
            [
                "usql",
                "--command",
                "SELECT 1;",
                "postgres://user:password@localhost:10510/database",
            ]
        ),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def howlite() -> AsyncGenerator[AsyncDockerContainer]:
    """Howlite container."""

    async def _check() -> None:
        auth = BasicAuth(username="user", password="password")
        async with AsyncClient(base_url="http://localhost:10520", auth=auth) as client:
            response = await client.get("/user/calendar")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/howlite:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def beaver(
    sapphire: AsyncDockerContainer, howlite: AsyncDockerContainer
) -> AsyncGenerator[AsyncDockerContainer]:
    """Beaver container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10500") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/services/beaver:latest",
        network="host",
    )

    waiter = Waiter(
        condition=CallableCondition(_check),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def client(
    app: Litestar,
    numbat: AsyncDockerContainer,
    gecko: AsyncDockerContainer,
    beaver: AsyncDockerContainer,
    octopus: AsyncDockerContainer,
) -> AsyncGenerator[AsyncTestClient]:
    """Reusable test client."""

    async with AsyncTestClient(app=app) as client:
        yield client

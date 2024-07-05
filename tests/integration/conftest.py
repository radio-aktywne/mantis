import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import pytest_asyncio
from httpx import AsyncClient, BasicAuth
from litestar import Litestar
from litestar.testing import AsyncTestClient
from minio import Minio

from emischeduler.api.app import AppBuilder
from emischeduler.config.builder import ConfigBuilder
from emischeduler.config.models import Config
from tests.utils.containers import AsyncDockerContainer
from tests.utils.waiting.conditions import CallableCondition, CommandCondition
from tests.utils.waiting.strategies import TimeoutStrategy
from tests.utils.waiting.waiter import Waiter


@pytest.fixture(scope="session")
def path() -> Path:
    """Path to the store file."""

    with TemporaryDirectory() as directory:
        yield Path(directory) / "state.json"


@pytest.fixture(scope="session")
def config(path: Path) -> Config:
    """Loaded configuration."""

    return ConfigBuilder(overrides=[f"store.path={path}"]).build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Reusable application."""

    return AppBuilder(config).build()


@pytest_asyncio.fixture(scope="session")
async def streamcast() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Streamcast container."""

    async def _check() -> None:
        auth = BasicAuth(username="admin", password="password")
        async with AsyncClient(base_url="http://localhost:8000", auth=auth) as client:
            response = await client.get("/admin/stats.json")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/streamcast:latest",
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
async def fusion(
    streamcast: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer, None]:
    """Fusion container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/fusion:latest",
        network="host",
    )

    async with container as container:
        await asyncio.sleep(5)
        yield container


@pytest_asyncio.fixture(scope="session")
async def emistream(
    fusion: AsyncDockerContainer,
) -> AsyncGenerator[AsyncDockerContainer, None]:
    """Emistream container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:10000") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emistream:latest",
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
async def datarecords() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Datarecords container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:30000") as client:
            response = await client.get("/minio/health/ready")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/datarecords:latest",
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
async def datashows() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Datashows container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/datashows:latest",
        network="host",
        privileged=True,
    )

    waiter = Waiter(
        condition=CommandCondition(
            [
                "usql",
                "--command",
                "SELECT 1;",
                "postgres://user:password@localhost:34000/database",
            ]
        ),
        strategy=TimeoutStrategy(30),
    )

    async with container as container:
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def datatimes() -> AsyncGenerator[AsyncDockerContainer, None]:
    """Datatimes container."""

    async def _check() -> None:
        auth = BasicAuth(username="user", password="password")
        async with AsyncClient(base_url="http://localhost:36000", auth=auth) as client:
            response = await client.get("/user/datatimes")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/databases/datatimes:latest",
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
async def emishows(
    datashows: AsyncDockerContainer, datatimes: AsyncDockerContainer
) -> AsyncGenerator[AsyncDockerContainer, None]:
    """Emishows container."""

    async def _check() -> None:
        async with AsyncClient(base_url="http://localhost:35000") as client:
            response = await client.get("/ping")
            response.raise_for_status()

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emishows:latest",
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
async def emishows_client(
    emishows: AsyncDockerContainer,
) -> AsyncGenerator[AsyncClient, None]:
    """Emishows client."""

    async with AsyncClient(base_url="http://localhost:35000") as client:
        yield client


@pytest.fixture(scope="session")
def datarecords_client(datarecords: AsyncDockerContainer) -> Minio:
    """Datarecords client."""

    return Minio(
        endpoint="localhost:30000",
        access_key="readwrite",
        secret_key="password",
        secure=False,
        cert_check=False,
    )


@pytest_asyncio.fixture(scope="session")
async def client(
    app: Litestar,
    emishows: AsyncDockerContainer,
    datarecords: AsyncDockerContainer,
    emistream: AsyncDockerContainer,
) -> AsyncGenerator[AsyncTestClient, None]:
    """Reusable test client."""

    async with AsyncTestClient(app=app) as client:
        yield client

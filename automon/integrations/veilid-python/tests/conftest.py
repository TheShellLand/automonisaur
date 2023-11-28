"""Common test fixtures."""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from veilid.json_api import _JsonVeilidAPI

import veilid

from .api import VeilidTestConnectionError, api_connector

pytest_plugins = ("pytest_asyncio",)


async def simple_update_callback(update: veilid.VeilidUpdate):
    print(f"VeilidUpdate: {update}")


@pytest_asyncio.fixture
async def api_connection() -> AsyncGenerator[_JsonVeilidAPI, None]:
    try:
        api = await api_connector(simple_update_callback)
    except VeilidTestConnectionError:
        pytest.skip("Unable to connect to veilid-server.")
        return

    async with api:
        # purge routes to ensure we start fresh
        await api.debug("purge routes")

        yield api

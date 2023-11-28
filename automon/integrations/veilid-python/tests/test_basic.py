# Basic veilid tests

import socket

import pytest
import veilid

from .conftest import simple_update_callback


@pytest.mark.asyncio
async def test_connect(api_connection: veilid.VeilidAPI):
    pass


@pytest.mark.asyncio
async def test_get_node_id(api_connection: veilid.VeilidAPI):
    state = await api_connection.get_state()
    node_ids = state.config.config.network.routing_table.node_id

    assert len(node_ids) >= 1

    for node_id in node_ids:
        assert node_id[4] == ":"


@pytest.mark.asyncio
async def test_fail_connect():
    with pytest.raises(socket.gaierror) as exc:
        await veilid.json_api_connect("fuahwelifuh32luhwafluehawea", 1, simple_update_callback)

    assert exc.value.errno == socket.EAI_NONAME


@pytest.mark.asyncio
async def test_version(api_connection: veilid.VeilidAPI):
    v = await api_connection.veilid_version()
    print(f"veilid_version: {v.__dict__}")
    assert v.__dict__.keys() >= {"_major", "_minor", "_patch"}

    vstr = await api_connection.veilid_version_string()
    print(f"veilid_version_string: {vstr}")

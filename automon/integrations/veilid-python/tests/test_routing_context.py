# Routing context veilid tests

import asyncio
import os
import random
import sys

import pytest

import veilid

from .api import VeilidTestConnectionError, api_connector

##################################################################


@pytest.mark.asyncio
async def test_routing_contexts(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        pass

    rc = await api_connection.new_routing_context()
    async with rc:
        rcp = await rc.with_default_safety(release=False)
        async with rcp:
            pass

    rc = await (await api_connection.new_routing_context()).with_sequencing(
        veilid.Sequencing.ENSURE_ORDERED
    )
    async with rc:
        pass

    rc = await (await api_connection.new_routing_context()).with_safety(
        veilid.SafetySelection.safe(
            veilid.SafetySpec(None, 2, veilid.Stability.LOW_LATENCY, veilid.Sequencing.NO_PREFERENCE)
        )
    )
    await rc.release()

    rc = await (await api_connection.new_routing_context()).with_safety(
        veilid.SafetySelection.unsafe(veilid.Sequencing.PREFER_ORDERED)
    )
    await rc.release()


@pytest.mark.asyncio
async def test_routing_context_app_message_loopback():
    # Seriously, mypy?
    app_message_queue: asyncio.Queue = asyncio.Queue()

    async def app_message_queue_update_callback(update: veilid.VeilidUpdate):
        if update.kind == veilid.VeilidUpdateKind.APP_MESSAGE:
            await app_message_queue.put(update)

    try:
        api = await api_connector(app_message_queue_update_callback)
    except VeilidTestConnectionError:
        pytest.skip("Unable to connect to veilid-server.")
        return

    async with api:
        # purge routes to ensure we start fresh
        await api.debug("purge routes")

        # make a routing context that uses a safety route
        rc = await api.new_routing_context()
        async with rc:
            # make a new local private route
            prl, blob = await api.new_private_route()

            # import it as a remote route as well so we can send to it
            prr = await api.import_remote_private_route(blob)

            # send an app message to our own private route
            message = b"abcd1234"
            await rc.app_message(prr, message)

            # we should get the same message back
            update: veilid.VeilidUpdate = await asyncio.wait_for(
                app_message_queue.get(), timeout=10
            )

            assert isinstance(update.detail, veilid.VeilidAppMessage)
            assert update.detail.message == message


@pytest.mark.asyncio
async def test_routing_context_app_call_loopback():
    app_call_queue: asyncio.Queue = asyncio.Queue()

    async def app_call_queue_update_callback(update: veilid.VeilidUpdate):
        if update.kind == veilid.VeilidUpdateKind.APP_CALL:
            await app_call_queue.put(update)

    try:
        api = await api_connector(app_call_queue_update_callback)
    except VeilidTestConnectionError:
        pytest.skip("Unable to connect to veilid-server.")
        return

    async with api:
        # purge routes to ensure we start fresh
        await api.debug("purge routes")

        # make a routing context
        rc = await api.new_routing_context()
        async with rc:
            # make a new local private route
            prl, blob = await api.new_private_route()

            # import it as a remote route as well so we can send to it
            prr = await api.import_remote_private_route(blob)

            # send an app message to our own private route
            request = b"abcd1234"
            app_call_task = asyncio.create_task(rc.app_call(prr, request), name="app call task")

            # we should get the same request back
            update: veilid.VeilidUpdate = await asyncio.wait_for(app_call_queue.get(), timeout=10)
            appcall = update.detail

            assert isinstance(appcall, veilid.VeilidAppCall)
            assert appcall.message == request

            # now we reply to the request
            reply = b"qwer5678"
            await api.app_call_reply(appcall.call_id, reply)

            # now we should get the reply from the call
            result = await app_call_task
            assert result == reply


@pytest.mark.asyncio
async def test_routing_context_app_message_loopback_big_packets():
    app_message_queue: asyncio.Queue = asyncio.Queue()

    count_hack = [0]

    async def app_message_queue_update_callback(update: veilid.VeilidUpdate):
        if update.kind == veilid.VeilidUpdateKind.APP_MESSAGE:
            count_hack[0] += 1
            print(f"{count_hack[0]} ", end="")
            await app_message_queue.put(update)

    sent_messages: set[bytes] = set()

    try:
        api = await api_connector(app_message_queue_update_callback)
    except VeilidTestConnectionError:
        pytest.skip("Unable to connect to veilid-server.")
        return

    async with api:
        # purge routes to ensure we start fresh
        await api.debug("purge routes")

        # make a routing context that uses a safety route
        rc = await api.new_routing_context()
        async with rc:
            # make a new local private route
            prl, blob = await api.new_private_route()

            # import it as a remote route as well so we can send to it
            prr = await api.import_remote_private_route(blob)

            # do this test 1000 times
            for _ in range(1000):
                # send a random sized random app message to our own private route
                message = random.randbytes(random.randint(0, 32768))
                await rc.app_message(prr, message)

                sent_messages.add(message)

            # we should get the same messages back
            print(len(sent_messages))
            for n in range(len(sent_messages)):
                print(n)
                update: veilid.VeilidUpdate = await asyncio.wait_for(
                    app_message_queue.get(), timeout=10
                )
                assert isinstance(update.detail, veilid.VeilidAppMessage)

                assert update.detail.message in sent_messages


@pytest.mark.asyncio
async def test_routing_context_app_call_loopback_big_packets():
    count_hack = [0]

    app_call_queue: asyncio.Queue = asyncio.Queue()

    async def app_call_queue_update_callback(update: veilid.VeilidUpdate):
        if update.kind == veilid.VeilidUpdateKind.APP_CALL:
            await app_call_queue.put(update)

    async def app_call_queue_task_handler(api: veilid.VeilidAPI):
        while True:
            update = await app_call_queue.get()

            count_hack[0] += 1
            print(f"{count_hack[0]} ", end="", flush=True)

            await api.app_call_reply(update.detail.call_id, update.detail.message)

    try:
        api = await api_connector(app_call_queue_update_callback)
    except VeilidTestConnectionError:
        pytest.skip("Unable to connect to veilid-server.")
        return

    async with api:
        # purge routes to ensure we start fresh
        await api.debug("purge routes")

        app_call_task = asyncio.create_task(app_call_queue_task_handler(api), name="app call task")

        # make a routing context that uses a safety route
        rc = await (await api.new_routing_context()).with_sequencing(
            veilid.Sequencing.ENSURE_ORDERED
        )
        async with rc:
            # make a new local private route
            prl, blob = await api.new_custom_private_route(
                [veilid.CryptoKind.CRYPTO_KIND_VLD0], 
                veilid.Stability.RELIABLE, 
                veilid.Sequencing.ENSURE_ORDERED)

            # import it as a remote route as well so we can send to it
            prr = await api.import_remote_private_route(blob)

            # do this test 10 times
            for _ in range(10):
                # send a random sized random app message to our own private route
                message = random.randbytes(random.randint(0, 32768))
                out_message = await rc.app_call(prr, message)

                assert message == out_message

        app_call_task.cancel()


@pytest.mark.skipif(os.getenv("NOSKIP") != "1", reason="unneeded test, only for performance check")
@pytest.mark.asyncio
async def test_routing_context_app_message_loopback_bandwidth():
    app_message_queue: asyncio.Queue = asyncio.Queue()

    async def app_message_queue_update_callback(update: veilid.VeilidUpdate):
        if update.kind == veilid.VeilidUpdateKind.APP_MESSAGE:
            await app_message_queue.put(True)

    try:
        api = await api_connector(app_message_queue_update_callback)
    except VeilidTestConnectionError:
        pytest.skip("Unable to connect to veilid-server.")
        return

    async with api:
        # purge routes to ensure we start fresh
        await api.debug("purge routes")

        # make a routing context that uses a safety route
        rc = await api.new_routing_context()
        async with rc:
            # make a new local private route
            prl, blob = await api.new_private_route()

            # import it as a remote route as well so we can send to it
            prr = await api.import_remote_private_route(blob)

            # do this test 1000 times
            message = random.randbytes(16384)
            for _ in range(10000):
                # send a random sized random app message to our own private route
                await rc.app_message(prr, message)

            # we should get the same number of messages back (not storing all that data)
            for _ in range(10000):
                await asyncio.wait_for(app_message_queue.get(), timeout=10)

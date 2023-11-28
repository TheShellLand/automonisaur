# Routing context veilid tests

import veilid
import pytest
import asyncio
import json
from . import *

##################################################################
BOGUS_KEY = veilid.TypedKey.from_value(
    veilid.CryptoKind.CRYPTO_KIND_VLD0, veilid.PublicKey.from_bytes(b'                                '))


@pytest.mark.asyncio
async def test_get_dht_value_unopened(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        with pytest.raises(veilid.VeilidAPIError):
            out = await rc.get_dht_value(BOGUS_KEY, veilid.ValueSubkey(0), False)


@pytest.mark.asyncio
async def test_open_dht_record_nonexistent_no_writer(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        with pytest.raises(veilid.VeilidAPIError):
            out = await rc.open_dht_record(BOGUS_KEY, None)


@pytest.mark.asyncio
async def test_close_dht_record_nonexistent(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        with pytest.raises(veilid.VeilidAPIError):
            await rc.close_dht_record(BOGUS_KEY)


@pytest.mark.asyncio
async def test_delete_dht_record_nonexistent(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        with pytest.raises(veilid.VeilidAPIError):
            await rc.delete_dht_record(BOGUS_KEY)


@pytest.mark.asyncio
async def test_create_delete_dht_record_simple(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        rec = await rc.create_dht_record(
            veilid.DHTSchema.dflt(1), veilid.CryptoKind.CRYPTO_KIND_VLD0
        )
        await rc.close_dht_record(rec.key)
        await rc.delete_dht_record(rec.key)


@pytest.mark.asyncio
async def test_get_dht_value_nonexistent(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        rec = await rc.create_dht_record(veilid.DHTSchema.dflt(1))
        assert await rc.get_dht_value(rec.key, 0, False) == None
        await rc.close_dht_record(rec.key)
        await rc.delete_dht_record(rec.key)


@pytest.mark.asyncio
async def test_set_get_dht_value(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        rec = await rc.create_dht_record(veilid.DHTSchema.dflt(2))

        vd = await rc.set_dht_value(rec.key, 0, b"BLAH BLAH BLAH")
        assert vd == None

        vd2 = await rc.get_dht_value(rec.key, 0, False)
        assert vd2 != None

        vd3 = await rc.get_dht_value(rec.key, 0, True)
        assert vd3 != None

        vd4 = await rc.get_dht_value(rec.key, 1, False)
        assert vd4 == None

        print("vd2: {}", vd2.__dict__)
        print("vd3: {}", vd3.__dict__)

        assert vd2 == vd3

        await rc.close_dht_record(rec.key)
        await rc.delete_dht_record(rec.key)


@pytest.mark.asyncio
async def test_open_writer_dht_value(api_connection: veilid.VeilidAPI):
    rc = await api_connection.new_routing_context()
    async with rc:
        rec = await rc.create_dht_record(veilid.DHTSchema.dflt(2))
        key = rec.key
        owner = rec.owner
        secret = rec.owner_secret
        print(f"key:{key}")

        cs = await api_connection.get_crypto_system(rec.key.kind())
        async with cs:
            assert await cs.validate_key_pair(owner, secret)
            other_keypair = await cs.generate_key_pair()

        va = b"Qwertyuiop Asdfghjkl Zxcvbnm"
        vb = b"1234567890"
        vc = b"!@#$%^&*()"

        # Test subkey writes
        vdtemp = await rc.set_dht_value(key, 1, va)
        assert vdtemp == None

        vdtemp = await rc.get_dht_value(key, 1, False)
        assert vdtemp.data == va
        assert vdtemp.seq == 0
        assert vdtemp.writer == owner

        vdtemp = await rc.get_dht_value(key, 0, False)
        assert vdtemp == None

        vdtemp = await rc.set_dht_value(key, 0, vb)
        assert vdtemp == None

        vdtemp = await rc.get_dht_value(key, 0, True)
        assert vdtemp.data == vb

        vdtemp = await rc.get_dht_value(key, 1, True)
        assert vdtemp.data == va

        # Equal value should not trigger sequence number update
        vdtemp = await rc.set_dht_value(key, 1, va)
        assert vdtemp == None

        # Different value should trigger sequence number update
        vdtemp = await rc.set_dht_value(key, 1, vb)
        assert vdtemp == None

        # Now that we initialized some subkeys
        # and verified they stored correctly
        # Delete things locally and reopen and see if we can write
        # with the same writer key

        await rc.close_dht_record(key)
        await rc.delete_dht_record(key)

        rec = await rc.open_dht_record(key, veilid.KeyPair.from_parts(owner, secret))
        assert rec != None
        assert rec.key == key
        assert rec.owner == owner
        assert rec.owner_secret == secret
        assert rec.schema.kind == veilid.DHTSchemaKind.DFLT
        assert rec.schema.o_cnt == 2

        # Verify subkey 1 can be set before it is get but newer is available online
        vdtemp = await rc.set_dht_value(key, 1, vc)
        assert vdtemp != None
        assert vdtemp.data == vb
        assert vdtemp.seq == 1
        assert vdtemp.writer == owner

        # Verify subkey 1 can be set a second time and it updates because seq is newer
        vdtemp = await rc.set_dht_value(key, 1, vc)
        assert vdtemp == None

        # Verify the network got the subkey update with a refresh check
        vdtemp = await rc.get_dht_value(key, 1, True)
        assert vdtemp != None
        assert vdtemp.data == vc
        assert vdtemp.seq == 2
        assert vdtemp.writer == owner

        # Delete things locally and reopen and see if we can write
        # with a different writer key (should fail)

        await rc.close_dht_record(key)
        await rc.delete_dht_record(key)

        rec = await rc.open_dht_record(key, other_keypair)
        assert rec != None
        assert rec.key == key
        assert rec.owner == owner
        assert rec.owner_secret == None
        assert rec.schema.kind == veilid.DHTSchemaKind.DFLT
        assert rec.schema.o_cnt == 2

        # Verify subkey 1 can NOT be set because we have the wrong writer
        with pytest.raises(veilid.VeilidAPIError):
            vdtemp = await rc.set_dht_value(key, 1, va)

        # Verify subkey 0 can NOT be set because we have the wrong writer
        with pytest.raises(veilid.VeilidAPIError):
            vdtemp = await rc.set_dht_value(key, 0, va)

        # Clean up
        await rc.close_dht_record(key)
        await rc.delete_dht_record(key)

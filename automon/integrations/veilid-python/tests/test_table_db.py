# TableDB veilid tests

import pytest
import veilid
from veilid.api import CryptoSystem


TEST_DB = "__pytest_db"
TEST_NONEXISTENT_DB = "__pytest_nonexistent_db"


@pytest.mark.asyncio
async def test_delete_table_db_nonexistent(api_connection: veilid.VeilidAPI):
    deleted = await api_connection.delete_table_db(TEST_NONEXISTENT_DB)
    assert not deleted


@pytest.mark.asyncio
async def test_open_delete_table_db(api_connection: veilid.VeilidAPI):
    # delete test db if it exists
    await api_connection.delete_table_db(TEST_DB)

    tdb = await api_connection.open_table_db(TEST_DB, 1)
    async with tdb:
        # delete should fail since it is still open
        with pytest.raises(veilid.VeilidAPIErrorGeneric) as exc:
            await api_connection.delete_table_db(TEST_DB)
        # drop the db

    # now delete should succeed
    deleted = await api_connection.delete_table_db(TEST_DB)
    assert deleted


@pytest.mark.asyncio
async def test_open_twice_table_db(api_connection: veilid.VeilidAPI):
    # delete test db if it exists
    await api_connection.delete_table_db(TEST_DB)

    tdb = await api_connection.open_table_db(TEST_DB, 1)
    tdb2 = await api_connection.open_table_db(TEST_DB, 1)

    # delete should fail because open
    with pytest.raises(veilid.VeilidAPIErrorGeneric) as exc:
        await api_connection.delete_table_db(TEST_DB)
    await tdb.release()

    # delete should fail because open
    with pytest.raises(veilid.VeilidAPIErrorGeneric) as exc:
        await api_connection.delete_table_db(TEST_DB)
    await tdb2.release()

    # delete should now succeed
    deleted = await api_connection.delete_table_db(TEST_DB)
    assert deleted


@pytest.mark.asyncio
async def test_open_twice_table_db_store_load(api_connection: veilid.VeilidAPI):
    # delete test db if it exists
    await api_connection.delete_table_db(TEST_DB)

    tdb = await api_connection.open_table_db(TEST_DB, 1)
    async with tdb:
        tdb2 = await api_connection.open_table_db(TEST_DB, 1)
        async with tdb2:
            # store into first db copy
            await tdb.store(b"asdf", b"1234")
            # load from second db copy
            assert await tdb.load(b"asdf") == b"1234"

    # delete should now succeed
    deleted = await api_connection.delete_table_db(TEST_DB)
    assert deleted


@pytest.mark.asyncio
async def test_open_twice_table_db_store_delete_load(api_connection: veilid.VeilidAPI):
    # delete test db if it exists
    await api_connection.delete_table_db(TEST_DB)

    tdb = await api_connection.open_table_db(TEST_DB, 1)
    async with tdb:
        tdb2 = await api_connection.open_table_db(TEST_DB, 1)
        async with tdb2:
            # store into first db copy
            await tdb.store(b"asdf", b"1234")
            # delete from second db copy and clean up
            await tdb2.delete(b"asdf")

        # load from first db copy
        assert await tdb.load(b"asdf") == None

    # delete should now succeed
    deleted = await api_connection.delete_table_db(TEST_DB)
    assert deleted


@pytest.mark.asyncio
async def test_resize_table_db(api_connection: veilid.VeilidAPI):
    # delete test db if it exists
    await api_connection.delete_table_db(TEST_DB)

    tdb = await api_connection.open_table_db(TEST_DB, 1)
    async with tdb:
        # reopen the db with more columns should fail if it is already open
        with pytest.raises(veilid.VeilidAPIErrorGeneric) as exc:
            await api_connection.open_table_db(TEST_DB, 2)

    tdb2 = await api_connection.open_table_db(TEST_DB, 2)
    async with tdb2:
        # write something to second column
        await tdb2.store(b"qwer", b"5678", col=1)

        # reopen the db with fewer columns
        tdb = await api_connection.open_table_db(TEST_DB, 1)
        async with tdb:
            # Should fail access to second column
            with pytest.raises(veilid.VeilidAPIErrorGeneric) as exc:
                await tdb.load(b"qwer", col=1)

            # Should succeed with access to second column
            assert await tdb2.load(b"qwer", col=1) == b"5678"

    # now delete should succeed
    deleted = await api_connection.delete_table_db(TEST_DB)
    assert deleted

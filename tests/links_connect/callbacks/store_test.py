from links_connect.callbacks import MemoryStoreCallback, LoggerCallback, ConId, ConType, Direction
import logging

log = logging.getLogger(__name__)


def test_store_callback():
    store = MemoryStoreCallback(default_find_timeout=1.0)
    chain = LoggerCallback() + store

    log.info(f"io_timeout: {store.default_find_timeout}")
    assert store.default_find_timeout == 1.0
    store.default_find_timeout = 0.1
    log.info(f"io_timeout: {store.default_find_timeout}")
    assert store.default_find_timeout == 0.1
    con_id = ConId(ConType.Initiator, "clt")
    msg_inp_1 = {"one": 1, "two": 2, "three": 3}
    msg_inp_2 = {"four": 4, "five": 5, "six": 6}
    chain.on_recv(con_id, msg_inp_1)
    chain.on_recv(con_id, msg_inp_2)

    pad = 65
    # find last
    found = store.find()
    assert found is not None
    log.info(f"{'find()'.ljust(pad)}found: {found.msg}")
    assert msg_inp_2 == found.msg

    # find by name
    found = store.find(name="clt")
    assert found is not None
    log.info("{find} -> {found}".format(find="find(name='clt')".ljust(pad), found=found.msg))
    assert msg_inp_2 == found.msg
    
    # find with filter
    found = store.find(filter={"three": 3})
    assert found is not None
    log.info("{find} -> {found}".format(find="find(filter={{'three': 3}})".ljust(pad), found=found.msg))
    assert msg_inp_1 == found.msg

    # find by name with filter and direction
    found = store.find(name="clt", filter={"three": 3}, direction=Direction.RECV)
    assert found is not None
    log.info("{find} -> {found}".format(find="find(name='clt', filter={{'three': 3}}, direction=Direction.RECV)".ljust(pad), found=found.msg))

    # find with filter and name
    found = store.find(filter={"three": 3}, name="clt")
    assert found is not None
    log.info("{find} -> {found}".format(find="find(filter={{'three': 3}}, name='clt')".ljust(pad), found=found.msg))
    assert msg_inp_1 == found.msg

    # not found by name
    found = store.find(name="svc")
    log.info("{find} found: {found}".format(find="find(name='svc')".ljust(pad), found=found))

    # not found by filter
    found = store.find(filter={"three": 4})
    log.info("{find} -> {found}".format(find="find(filter={{'three': 4}})".ljust(pad), found=found))
    assert found is None


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])

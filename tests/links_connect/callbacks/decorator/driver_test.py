from links_connect.callbacks import (
    ConId,
    Message,
    on_recv,
    on_sent,
    DecoratorDriver,
    CallbackRegistry,
    LoggerCallback,
)
from links_connect.callbacks._04_decorator.driver import scope_name
import logging

log = logging.getLogger(__name__)


def test_callback_settable_sender_import():
    class ExampleCallback1(DecoratorDriver):
        pass

    from links_connect.callbacks import SettableSender
    from links_connect.callbacks._04_decorator.driver import Sender

    clbk = ExampleCallback1()
    assert isinstance(clbk, SettableSender)
    assert isinstance(clbk.sender, Sender)


def test_callback_driver():
    class ExampleCallback1(DecoratorDriver):
        def __init__(self):
            super().__init__()
            self._one_recv = 0
            self._two_recv = 0
            self._three_recv = 0
            self._one_sent = 0
            self._two_sent = 0
            self._three_sent = 0

        @on_recv(filter={"one_recv": {}})
        def one_recv(self, con_id: ConId, msg: Message):
            self._one_recv += 1

        @on_recv(filter={"two_recv": {}})
        def two_recv(self, con_id: ConId, msg: Message):
            self._two_recv += 1

        @on_sent(filter={"one_sent": {}})
        def one_sent(self, con_id: ConId, msg: Message):
            self._one_sent += 1

        @on_sent(filter={"two_sent": {}})
        def two_sent(self, con_id: ConId, msg: Message):
            self._two_sent += 1

    class ExampleCallback2(DecoratorDriver):
        def __init__(self):
            super().__init__()
            self._one_recv = 0

        @on_recv(filter={"one_recv": {}})
        def one_recv(self, con_id: ConId, msg: Message):
            self._one_recv += 1

    clbk1 = ExampleCallback1() + LoggerCallback()
    clbk2 = ExampleCallback2() + LoggerCallback()

    log.info(f"clbk: {clbk1}")
    log.info(f"clbk: {clbk2}")
    assert CallbackRegistry.get(scope_name(ExampleCallback1.one_recv)).on_recv_filter_callback_entries.len() == 2
    assert CallbackRegistry.get(scope_name(ExampleCallback1.one_recv)).on_sent_filter_callback_entries.len() == 2
    assert CallbackRegistry.get(scope_name(ExampleCallback2.one_recv)).on_recv_filter_callback_entries.len() == 1
    assert CallbackRegistry.get(scope_name(ExampleCallback2.one_recv)).on_sent_filter_callback_entries.len() == 0

    clbk1.on_recv(ConId(), {"one_recv": {}, "two_recv": {}, "three_recv": {}})
    clbk2.on_recv(ConId(), {"one_recv": {}, "two_recv": {}, "three_recv": {}})
    clbk1.on_sent(ConId(), {"one_sent": {}, "two_sent": {}, "three_sent": {}})
    assert clbk1._one_recv == 1  # called because it is the first @on_recv annotated method
    assert clbk1._two_recv == 0
    assert clbk1._three_recv == 0
    assert clbk1._one_sent == 1  # called because it is the first @on_recv annotated method
    assert clbk1._two_sent == 0
    assert clbk1._three_sent == 0
    assert clbk2._one_recv == 1  # called because it is the first @on_recv annotated method


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])

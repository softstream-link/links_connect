from links_core.callbacks import *
from links_core.callbacks.decorator import ScenarioCallbackDriver, on_recv, on_sent
import pytest

import logging

log = logging.getLogger(__name__)


class ExampleCallback(ScenarioCallbackDriver):
    def __init__(self):
        super().__init__()
        self._one_recv = 0
        self._two_recv = 0
        self._three_recv = 0
        self._one_sent = 0
        self._two_sent = 0
        self._three_sent = 0

    def one_recv(self, con_id: ConId, msg: MsgDict):
        log.info(f"{ExampleCallback.__name__}.one_recv: called with {con_id} {msg}")
        self._one_recv += 1

    @on_recv(filter={"two_recv": {}}, registry=ScenarioCallbackDriver)
    def two_recv(self, con_id: ConId, msg: MsgDict):
        log.info(f"{ExampleCallback.__name__}.two_recv: called with {con_id} {msg}")
        self._two_recv += 1

    @on_recv(filter={"three_recv": {}}, registry=ScenarioCallbackDriver)
    def three_recv(self, con_id: ConId, msg: MsgDict):
        log.info(f"{ExampleCallback.__name__}.three_recv: called with {con_id} {msg}")
        self._three_recv += 1

    def one_sent(self, con_id: ConId, msg: MsgDict):
        log.info(f"{ExampleCallback.__name__}.one_sent: called with {con_id} {msg}")
        self._one_sent += 1

    @on_sent(filter={"two_sent": {}}, registry=ScenarioCallbackDriver)
    def two_sent(self, con_id: ConId, msg: MsgDict):
        log.info(f"{ExampleCallback.__name__}.two_sent: called with {con_id} {msg}")
        self._two_sent += 1

    @on_sent(filter={"three_sent": {}}, registry=ScenarioCallbackDriver)
    def three_sent(self, con_id: ConId, msg: MsgDict):
        log.info(f"{ExampleCallback.__name__}.three_sent: called with {con_id} {msg}")
        self._three_sent += 1


def test_scenario_callback_driver():
    clbk = ExampleCallback()
    clbk.registry_on_recv.push({"one_recv": {}}, clbk.one_recv)

    clbk.registry_on_sent.push({"one_sent": {}}, clbk.one_sent)

    log.info(f"clbk: {clbk}")
    assert clbk.registry_on_recv.len() == 3
    assert clbk.registry_on_sent.len() == 3

    clbk.on_recv(ConId(), {"one_recv": {}, "two_recv": {}, "three_recv": {}})
    clbk.on_sent(ConId(), {"one_sent": {}, "two_sent": {}, "three_sent": {}})
    assert clbk._one_recv == 0
    assert clbk._two_recv == 1 # called because it is the first @on_recv annotated method
    assert clbk._three_recv == 0
    assert clbk._one_sent == 0
    assert clbk._two_sent == 1 # called because it is the first @on_recv annotated method
    assert clbk._three_sent == 0



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_scenario_callback_driver()
    # pytest.main([__file__])  # fails because ExampleCallback get loaded twice which causes callbacks to be registered twice

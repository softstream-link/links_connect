from links_connect.callbacks.decorator.registry import FilterCallbackEntries, FilterEntry, CallbackRegistry
import pytest
import logging

log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "filter, data, is_matching",
    [
        ({}, {"one": 1}, True),
        ({"one": 1}, {"one": 1}, True),
        ({"one": {}}, {"one": {"two": "2"}}, True),
        ({"one": 1, "two": 2}, {"one": 1, "two": 2, "three": 3}, True),
        ({"one": 1, "two": 2, "three": 3}, {"one": 1, "two": 2}, False),
        ({"one": 1}, {"one": "1"}, False),
        ({"one": {}}, {"one": ""}, False),
        ({"one": ""}, {"one": {}}, False),
        ({"one": {}}, {"one": []}, False),
    ],
)
def test_is_subset(filter, data, is_matching):
    log.info(f"filter: {filter}")
    log.info(f"data: {data}")
    log.info(f"is_matching: {is_matching}")

    entry = FilterEntry(filter, lambda clbk, con_id, msg: None)
    assert entry.is_matching(data) == is_matching


def test_callback_function_filter_entries():
    registry = FilterCallbackEntries()
    one = lambda clbk, con_id, msg: None
    two = lambda clbk, con_id, msg: None

    registry.push({"one": 1}, one)
    registry.push({"two": 2}, two)

    assert registry.len() == 2
    log.info(f"\n{registry}")

    assert registry.find({"one": 1}) == one
    assert registry.find({"two": 2}) == two
    assert registry.find({"one": 1, "two": 2}) == one
    assert registry.find({"two": 2, "one": 1}) == one
    assert registry.find_all({"two": 2, "one": 1}) == [one, two]
    assert registry.find({}) == None

def test_callback_registry():
    
    assert CallbackRegistry.len() == 0
    registry1 = CallbackRegistry.get("one")
    registry1_ = CallbackRegistry.get("one")
    assert registry1 == registry1_
    registry2 = CallbackRegistry.get("two")
    registry3 = CallbackRegistry.get("three")
    
    one = lambda clbk, con_id, msg: None
    two = lambda clbk, con_id, msg: None
    three = lambda clbk, con_id, msg: None

    registry1.on_recv_filter_callback_entries.push({"one": 1}, one)
    registry2.on_recv_filter_callback_entries.push({"two": 1}, two)

    log.info(f"{registry1!s}") # includes self instance
    log.info(f"{registry1!r}") # includes cls instance

if __name__ == "__main__":
    pytest.main([__file__])

from links_core.callbacks.decorator.registry import *
import pytest
import logging

log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "filter, data, is_subset",
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
def test_is_subset(filter, data, is_subset):
    log.info(f"filter: {filter}")
    log.info(f"data: {data}")
    log.info(f"is_subset: {is_subset}")
    assert in_subset(filter, data) == is_subset


def test_callback_registry():
    registry = CallbackRegistry()
    one = lambda: 1
    two = lambda: 2

    registry.push({"one": 1}, one)
    registry.push({"two": 2}, two)

    assert registry.len() == 2
    log.info(f"\n{registry}")

    assert registry.find({"one": 1}).function() == one()
    assert registry.find({"two": 2}).function() == two()
    assert registry.find({"one": 1, "two": 2}).function() == one()
    assert registry.find({"two": 2, "one": 1}).function() == one()
    assert registry.find_all({"two": 2, "one": 1}) == [Entry({"one": 1}, one), Entry({"two": 2}, two)]
    assert registry.find({}) == None


if __name__ == "__main__":
    pytest.main([__file__])

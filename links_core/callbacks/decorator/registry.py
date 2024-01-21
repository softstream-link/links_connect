from dataclasses import dataclass
import logging
from typing import Union

Data = dict
Filter = dict
Function = callable

log = logging.getLogger(__name__)


def in_subset(filter: Filter, data: Data) -> bool:
    for f_key, f_val in filter.items():
        match data.get(f_key, None):
            case None:
                return True if f_val is None else False
            case dict() as d_val:
                if (not isinstance(f_val, dict)) or (isinstance(f_val, dict) and not in_subset(f_val, d_val)):
                    return False
            case _ as d_val:
                if f_val != d_val:
                    return False

    return True


@dataclass
class Entry:
    filter: Filter
    function: Function


class CallbackRegistry:
    def __init__(self):
        self._registry: list[Entry] = []

    def len(self) -> int:
        return len(self._registry)

    def push(self, filter: Filter, function: Function):
        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"{self.__class__.__name__}.push: filter: {filter}, function: {function}")
        self._registry.append(Entry(filter, function))

    def find_all(self, data: Data) -> list[Entry]:
        return [entry for entry in self._registry if in_subset(entry.filter, data)]

    def find(self, data: Data) -> Entry | None:
        for entry in self._registry:
            if in_subset(entry.filter, data):
                return entry
        return None

    def get(self, filter: Filter) -> Union[Function, None]:
        for entry in self._registry:
            if entry.filter == filter:
                return entry.function
        return None

    def __iter__(self):
        return iter(self._registry)

    def __str__(self) -> str:
        return f'\n\tfilters: #{self.len()} {super().__str__()}\n\t{"\n\t".join([str(entry) for entry in self._registry])}'

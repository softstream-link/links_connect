import links_connect as lc
import logging
from typing import Callable, Optional, List
from collections.abc import Sequence
from dataclasses import dataclass


log = logging.getLogger(__name__)


class DecoratorDriverBase(lc.Chainable):
    def __init__(self):
        super().__init__()


CallbackFunction = Callable[[DecoratorDriverBase, lc.ConId, lc.Message], None]


@dataclass
class FilterEntry:
    filter: lc.Filter
    function: CallbackFunction


class FilterCallbackEntries:
    def __init__(self):
        self.__filter_entries: List[FilterEntry] = []

    def len(self) -> int:
        return len(self.__filter_entries)

    def push(self, subset: lc.Filter, function: CallbackFunction):
        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"{self.__class__.__name__}.push: filter: {subset}, function: {function}")
        self.__filter_entries.append(FilterEntry(subset, function))

    def find_all(self, message: lc.Message) -> List[CallbackFunction]:
        return [entry.function for entry in self.__filter_entries if lc.is_matching(entry.filter, message)]

    def find(self, message: lc.Message) -> Optional[CallbackFunction]:
        for entry in self.__filter_entries:
            if lc.is_matching(entry.filter, message):
                return entry.function
        return None

    def get(self, subset: lc.Filter) -> Optional[CallbackFunction]:
        for entry in self.__filter_entries:
            if entry.filter == subset:
                return entry.function
        return None

    @property
    def entries(self) -> Sequence[FilterEntry]:
        return self.__filter_entries

    def __iter__(self):
        return iter(self.__filter_entries)

    def __str__(self) -> str:
        return f'filters: #{self.len()} {super().__str__()}\n{"\n".join([str(entry) for entry in self.entries])}'


from typing import Dict, Self


class CallbackRegistry:
    __callback_registries: Dict[str, Self] = {}

    @classmethod
    def get(cls, name: str) -> "CallbackRegistry":
        if name not in cls.__callback_registries.keys():
            cls.__callback_registries[name] = cls(name)

        return cls.__callback_registries[name]

    @classmethod
    @property
    def registries(cls) -> Dict[str, Self]:
        return cls.__callback_registries

    @classmethod
    def len(cls) -> int:
        return len(cls.__callback_registries)

    def __init__(self, name: str) -> None:
        self.__name = name
        self.__on_recv_filter_callback_entries = FilterCallbackEntries()
        self.__on_sent_filter_callback_entries = FilterCallbackEntries()

    @property
    def on_recv_filter_callback_entries(self) -> FilterCallbackEntries:
        return self.__on_recv_filter_callback_entries

    @property
    def on_sent_filter_callback_entries(self) -> FilterCallbackEntries:
        return self.__on_sent_filter_callback_entries

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.__name}):"
            + f"\non_recv -> len: {self.on_recv_filter_callback_entries.len()}"
            + f"{'\n' if self.on_recv_filter_callback_entries.len() else ''}{'\n'.join(['\t' + str(e) for e in self.on_recv_filter_callback_entries.entries] )}"
            + f"\non_sent -> len: {self.on_sent_filter_callback_entries.len()}"
            + f"{'\n' if self.on_sent_filter_callback_entries.len() else ''}{'\n'.join(['\t' + str(e) for e in self.on_sent_filter_callback_entries.entries])}\n"
        )

    def __repr__(self) -> str:
        from io import StringIO

        buf = StringIO()
        buf.write(f"{self.__class__.__name__} -> len: {len(self.__callback_registries)}\n")
        for k, v in self.__callback_registries.items():
            buf.write(f"{v}\n")
        return f"{buf.getvalue()}"

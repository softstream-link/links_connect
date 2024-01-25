from links_connect.callbacks import Callback, ConId, Message, Filter
import logging
from typing import Callable, Type, Any, Optional, List
from collections.abc import Sequence
from dataclasses import dataclass


log = logging.getLogger(__name__)


class DecoratorBase(Callback):
    pass


CallbackFunction = Callable[[DecoratorBase, ConId, Message], None]


@dataclass
class FilterEntry:
    filter: Filter
    function: CallbackFunction

    def is_matching(self, data: Message) -> bool:
        for f_key, f_val in self.filter.items():
            match data.get(f_key, None):
                case None:
                    return True if f_val is None else False
                case dict() as d_val:
                    if (not isinstance(f_val, dict)) or (isinstance(f_val, dict) and len(f_val) != 0 and not self.is_matching(d_val)):
                        return False
                case _ as d_val:
                    if f_val != d_val:
                        return False

        return True


class FilterCallbackEntries:
    def __init__(self):
        self._filter_entries: List[FilterEntry] = []

    def len(self) -> int:
        return len(self._filter_entries)

    def push(self, subset: Filter, function: CallbackFunction):
        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"{self.__class__.__name__}.push: filter: {subset}, function: {function}")
        self._filter_entries.append(FilterEntry(subset, function))

    def find_all(self, message: Message) -> List[CallbackFunction]:
        return [entry.function for entry in self._filter_entries if entry.is_matching(message)]

    def find(self, message: Message) -> Optional[CallbackFunction]:
        for entry in self._filter_entries:
            if entry.is_matching(message):
                return entry.function
        return None

    def get(self, subset: Filter) -> Optional[CallbackFunction]:
        for entry in self._filter_entries:
            if entry.filter == subset:
                return entry.function
        return None

    @property
    def entries(self) -> Sequence[FilterEntry]:
        return self._filter_entries

    def __iter__(self):
        return iter(self._filter_entries)

    def __str__(self) -> str:
        return f'filters: #{self.len()} {super().__str__()}\n{"\n".join([str(entry) for entry in self.entries])}'


from typing import Dict, Self


class CallbackRegistry:
    _callback_registries: Dict[str, Self] = {}

    @classmethod
    def get(cls, name: str) -> "CallbackRegistry":
        if name not in cls._callback_registries.keys():
            cls._callback_registries[name] = cls(name)

        return cls._callback_registries[name]

    @classmethod
    @property
    def registries(cls) -> Dict[str, Self]:
        return cls._callback_registries

    @classmethod
    def len(cls) -> int:
        return len(cls._callback_registries)

    def __init__(self, name: str) -> None:
        self._name = name
        self._on_recv_filter_callback_entries = FilterCallbackEntries()
        self._on_sent_filter_callback_entries = FilterCallbackEntries()

    @property
    def on_recv_filter_callback_entries(self) -> FilterCallbackEntries:
        return self._on_recv_filter_callback_entries

    @property
    def on_sent_filter_callback_entries(self) -> FilterCallbackEntries:
        return self._on_sent_filter_callback_entries

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self._name}):"
            + f"\non_recv -> len: {self.on_recv_filter_callback_entries.len()}"
            + f"{'\n' if self.on_recv_filter_callback_entries.len() else ''}{'\n'.join(['\t' + str(e) for e in self.on_recv_filter_callback_entries.entries] )}"
            + f"\non_sent -> len: {self.on_sent_filter_callback_entries.len()}"
            + f"{'\n' if self.on_sent_filter_callback_entries.len() else ''}{'\n'.join(['\t' + str(e) for e in self.on_sent_filter_callback_entries.entries])}\n"
        )

    def __repr__(self) -> str:
        from io import StringIO
        buf = StringIO()
        buf.write(f"{self.__class__.__name__} -> len: {len(self._callback_registries)}\n")
        for k, v in self._callback_registries.items():
            buf.write(f"{v}\n")
        return f"{buf.getvalue()}"
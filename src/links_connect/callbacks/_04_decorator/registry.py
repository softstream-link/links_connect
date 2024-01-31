import links_connect.callbacks as clbks
import logging
import typing
import dataclasses

log = logging.getLogger(__name__)


class DecoratorDriverBase(clbks.ChainableCallback):
    def __init__(self):
        super().__init__()


CallbackFunction = typing.Callable[[DecoratorDriverBase, clbks.ConId, clbks.Message], None]


@dataclasses.dataclass
class Filter2CallbackEntry:
    filter: clbks.Filter
    function: CallbackFunction


class Filter2CallbackEntries:
    def __init__(self):
        self.__filter_entries: typing.List[Filter2CallbackEntry] = []

    def len(self) -> int:
        return len(self.__filter_entries)

    def push(self, subset: clbks.Filter, function: CallbackFunction):
        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"{self.__class__.__name__}.push: filter: {subset}, function: {function}")
        self.__filter_entries.append(Filter2CallbackEntry(subset, function))

    def find_all(self, message: clbks.Message) -> typing.List[CallbackFunction]:
        return [entry.function for entry in self.__filter_entries if clbks.is_matching(entry.filter, message)]

    def find(self, message: clbks.Message) -> typing.Optional[CallbackFunction]:
        for entry in self.__filter_entries:
            if clbks.is_matching(entry.filter, message):
                return entry.function
        return None

    def get(self, subset: clbks.Filter) -> typing.Optional[CallbackFunction]:
        for entry in self.__filter_entries:
            if entry.filter == subset:
                return entry.function
        return None

    @property
    def entries(self) -> typing.Iterable[Filter2CallbackEntry]:
        return self.__filter_entries

    def __iter__(self):
        return iter(self.__filter_entries)

    def __str__(self) -> str:
        return "filters: #{len} {name}\n{entries}".format(
            len=self.len(),
            name=super().__str__(),
            entries="\n".join([str(entry) for entry in self.entries]),
        )


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
        self.__on_recv_filter_callback_entries = Filter2CallbackEntries()
        self.__on_sent_filter_callback_entries = Filter2CallbackEntries()

    @property
    def on_recv_filter_callback_entries(self) -> Filter2CallbackEntries:
        return self.__on_recv_filter_callback_entries

    @property
    def on_sent_filter_callback_entries(self) -> Filter2CallbackEntries:
        return self.__on_sent_filter_callback_entries

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.__name}):"
            + "\non_recv -> len: {len}".format(len=self.on_recv_filter_callback_entries.len())
            + "{nl}{entries}".format(
                nl="\n" if self.on_recv_filter_callback_entries.len() else "",
                entries="\n".join(["\t" + str(e) for e in self.on_recv_filter_callback_entries.entries]),
            )
            + "\non_sent -> len: {len}".format(len=self.on_sent_filter_callback_entries.len())
            + "{nl}{entries}\n".format(
                nl="\n" if self.on_sent_filter_callback_entries.len() else "",
                entries="\n".join(["\t" + str(e) for e in self.on_sent_filter_callback_entries.entries]),
            )
        )

    def __repr__(self) -> str:
        from io import StringIO

        buf = StringIO()
        buf.write(f"{self.__class__.__name__} -> len: {len(self.__callback_registries)}\n")
        for k, v in self.__callback_registries.items():
            buf.write(f"{v}\n")
        return f"{buf.getvalue()}"

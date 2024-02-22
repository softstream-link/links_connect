from links_connect.callbacks import (
    ConId,
    Message,
    Filter,
    is_matching,
    ChainableCallback,
)
import dataclasses
import enum
import datetime as dt
import typing as ty
import time
import abc
import time
import itertools as it


class Direction(enum.Enum):
    SENT = enum.auto()
    RECV = enum.auto()


@dataclasses.dataclass
class Entry:
    direction: Direction
    datetimestamp: dt.datetime
    con_id: ConId
    msg: Message


class Store(metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()

    @property
    @abc.abstractmethod
    def reversed_store(self) -> ty.Iterator[Entry]: ...

    @property
    @abc.abstractmethod
    def default_find_timeout(self) -> ty.Optional[float]: ...

    def effective_timeout(self, io_timeout: ty.Optional[float]) -> float:
        if io_timeout is not None:
            return io_timeout
        elif self.default_find_timeout is not None:
            return self.default_find_timeout
        else:
            return 0.0

    def find(
        self,
        name: ty.Optional[str] = None,
        filter: ty.Optional[Filter] = None,
        direction: ty.Optional[Direction] = None,
        find_timeout: ty.Optional[float] = None,
    ) -> ty.Optional[Entry]:
        filter = {} if filter is None else filter
        now = time.time()
        find_timeout = self.effective_timeout(find_timeout)

        while True:
            for entry in self.reversed_store:
                name_match = name is None or entry.con_id.name == name
                filter_match = is_matching(filter, entry.msg)
                direction_match = direction is None or entry.direction == direction

                if name_match and filter_match and direction_match:
                    return entry

            time.sleep(0.0001)
            if time.time() - now > find_timeout:
                return None

    def find_recv(
        self,
        name: ty.Optional[str] = None,
        filter: ty.Optional[Filter] = None,
        find_timeout: ty.Optional[float] = None,
    ) -> ty.Optional[Entry]:
        return self.find(name, filter, Direction.RECV, find_timeout)

    def find_sent(
        self,
        name: ty.Optional[str] = None,
        filter: ty.Optional[Filter] = None,
        find_timeout: ty.Optional[float] = None,
    ) -> ty.Optional[Entry]:
        return self.find(name, filter, Direction.SENT, find_timeout)

    def find_all(
        self,
        name: ty.Optional[str] = None,
        filter: ty.Optional[Filter] = None,
        direction: ty.Optional[Direction] = None,
        find_timeout: ty.Optional[float] = None,
        top: ty.Optional[int] = None,
    ) -> ty.List[Entry]:
        filter = {} if filter is None else filter
        now = time.time()

        while True:
            result: ty.List[Entry] = []
            for entry in self.reversed_store:
                if (
                    (name is None or entry.con_id.name == name)
                    and is_matching(filter, entry.msg)
                    and (direction is None or entry.direction == direction)
                ):
                    result.append(entry)
                    if top is not None and len(result) >= top:
                        return result

            if len(result) > 0:
                return result
            if time.time() - now > self.effective_timeout(find_timeout):
                return result

    def find_all_recv(
        self,
        name: ty.Optional[str] = None,
        filter: ty.Optional[Filter] = None,
        find_timeout: ty.Optional[float] = None,
        top: ty.Optional[int] = None,
    ) -> ty.List[Entry]:
        return self.find_all(name, filter, Direction.RECV, find_timeout, top)

    def find_all_sent(
        self,
        name: ty.Optional[str] = None,
        filter: ty.Optional[Filter] = None,
        find_timeout: ty.Optional[float] = None,
        top: ty.Optional[int] = None,
    ) -> ty.List[Entry]:
        return self.find_all(name, filter, Direction.SENT, find_timeout, top)


class MemoryStoreCallback(Store, ChainableCallback):
    def __init__(self, default_find_timeout: ty.Optional[float] = None):
        super().__init__()
        self.__store: ty.List[Entry] = []
        self.__default_find_timeout = default_find_timeout

    def on_recv(self, con_id: ConId, msg: Message) -> None:
        self.__store.append(Entry(Direction.RECV, dt.datetime.now(), con_id, msg))
        super().on_recv(con_id, msg)

    def on_sent(self, con_id: ConId, msg: Message) -> None:
        self.__store.append(Entry(Direction.SENT, dt.datetime.now(), con_id, msg))
        super().on_sent(con_id, msg)

    @property
    def reversed_store(self) -> ty.Iterator[Entry]:
        return reversed(self.__store)

    @property
    def default_find_timeout(self) -> ty.Optional[float]:
        return self.__default_find_timeout

    @default_find_timeout.setter
    def default_find_timeout(self, default_find_timeout: float):
        self.__default_find_timeout = default_find_timeout

    def __str__(self) -> str:
        return self.state(None)

    def __len__(self) -> int:
        return len(self.__store)

    def state(self, name: ty.Optional[str] = None, direction: ty.Optional[Direction] = None) -> str:
        from io import StringIO

        buf = StringIO()
        matching = self.find_all(name=name, direction=direction)
        buf.write(f"{self.__class__.__name__} -> {len(matching):,} of {len(self.__store):,}\n")
        for e in matching:
            if (name is not None and e.con_id.name != name) or (direction is not None and e.direction != direction):
                continue
            timestamp_fmt = e.datetimestamp.strftime("%H:%M:%S.%f")
            direction_fmt = "SENT" if e.direction == Direction.SENT else "RECV"
            buf.write(f"{timestamp_fmt} {direction_fmt} {e.con_id} \t{e.msg} \n")
        return f"{buf.getvalue()}"

    def clear(self, name: ty.Optional[str] = None):
        if name is None:
            self.__store.clear()
        else:
            # [:] will mutate the list rather then creating a new list object
            self.__store[:] = it.dropwhile(lambda e: e.con_id.name == name, self.__store)

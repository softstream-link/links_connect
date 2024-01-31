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


class Direction(enum.Enum):
    SENT = enum.auto()
    RECV = enum.auto()


@dataclasses.dataclass
class Entry:
    direction: Direction
    timestamp: dt.datetime
    con_id: ConId
    msg: Message


class Store(metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()

    @property
    @abc.abstractmethod
    def reversed_store(self) -> ty.Iterator[Entry]:
        ...

    @property
    @abc.abstractmethod
    def io_timeout(self) -> ty.Optional[float]:
        ...

    def __effective_timeout(self, io_timeout: ty.Optional[float]) -> float:
        return (
            io_timeout
            if io_timeout is not None
            else (self.io_timeout if self.io_timeout is not None else 0)
        )

    def find(
        self,
        name: ty.Optional[str] = None,
        filter: ty.Optional[Filter] = None,
        direction: ty.Optional[Direction] = None,
        io_timeout: ty.Optional[float] = None,
    ) -> ty.Optional[Entry]:
        filter = {} if filter is None else filter
        now = time.time()

        while True:
            for entry in self.reversed_store:
                if (
                    (name is None or entry.con_id.name == name)
                    and is_matching(filter, entry.msg)
                    and (direction is None or entry.direction == direction)
                ):
                    return entry
            if time.time() - now > self.__effective_timeout(io_timeout):
                return None

    def find_recv(
        self,
        name: ty.Optional[str],
        filter: ty.Optional[Filter] = None,
        io_timeout: ty.Optional[float] = None,
    ) -> ty.Optional[Entry]:
        return self.find(name, filter, Direction.RECV, io_timeout)

    def find_sent(
        self,
        name: ty.Optional[str],
        filter: ty.Optional[Filter] = None,
        io_timeout: ty.Optional[float] = None,
    ) -> ty.Optional[Entry]:
        return self.find(name, filter, Direction.SENT, io_timeout)

    def find_all(
        self,
        name: ty.Optional[str],
        filter: ty.Optional[Filter] = None,
        direction: ty.Optional[Direction] = None,
        io_timeout: ty.Optional[float] = None,
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
            if time.time() - now > self.__effective_timeout(io_timeout):
                return result

    def find_all_recv(
        self,
        name: ty.Optional[str],
        filter: ty.Optional[Filter] = None,
        io_timeout: ty.Optional[float] = None,
        top: ty.Optional[int] = None,
    ) -> ty.List[Entry]:
        return self.find_all(name, filter, Direction.RECV, io_timeout, top)

    def find_all_sent(
        self,
        name: ty.Optional[str],
        filter: ty.Optional[Filter] = None,
        io_timeout: ty.Optional[float] = None,
        top: ty.Optional[int] = None,
    ) -> ty.List[Entry]:
        return self.find_all(name, filter, Direction.SENT, io_timeout, top)


class MemoryStoreCallback(Store, ChainableCallback):
    def __init__(self, io_timeout: ty.Optional[float] = 1.0):
        super().__init__()
        self.__store: ty.List[Entry] = []
        self.__io_timeout = io_timeout

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
    def io_timeout(self) -> ty.Optional[float]:
        return self.__io_timeout

    # @property
    @io_timeout.setter
    def io_timeout(self, io_timeout: float) -> None:
        self.__io_timeout = io_timeout

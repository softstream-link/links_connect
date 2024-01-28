import links_connect as lc
from links_connect.callbacks import ConId, Filter, Message
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime
import time
from typing import List, Optional, Iterator
from abc import ABCMeta, abstractmethod


class Direction(Enum):
    SENT = auto()
    RECV = auto()


@dataclass
class Entry:
    direction: Direction
    timestamp: datetime
    con_id: ConId
    msg: Message


class Store(metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def reversed_store(self) -> Iterator[Entry]:
        ...

    @property
    @abstractmethod
    def io_timeout(self) -> Optional[float]:
        ...

    def __effective_timeout(self, io_timeout: Optional[float]) -> float:
        return io_timeout if io_timeout is not None else (self.io_timeout if self.io_timeout is not None else 0)

    def find(
        self,
        name: Optional[str] = None,
        filter: Optional[lc.Filter] = None,
        direction: Optional[Direction] = None,
        io_timeout: Optional[float] = None,
    ) -> Optional[Entry]:
        filter = {} if filter is None else filter
        now = time.time()

        while True:
            for entry in self.reversed_store:
                if (
                    (name is None or entry.con_id.name == name)
                    and lc.is_matching(filter, entry.msg)
                    and (direction is None or entry.direction == direction)
                ):
                    return entry
            if time.time() - now > self.__effective_timeout(io_timeout):
                return None

    def find_recv(self, name: str, filter: Optional[lc.Filter] = None, io_timeout: Optional[float] = None) -> Optional[Entry]:
        return self.find(name, filter, Direction.RECV, io_timeout)

    def find_sent(self, name: str, filter: Optional[lc.Filter] = None, io_timeout: Optional[float] = None) -> Optional[Entry]:
        return self.find(name, filter, Direction.SENT, io_timeout)

    # @abstractmethod
    # def find_all(
    #     self, name: str, filter: Optional[lc.Filter] = None, direction: Optional[Direction] = None, io_timeout: Optional[float] = None
    # ) -> List[Entry]:
    #     ...

    # def find_all_recv(self, name: str, filter: Optional[lc.Filter] = None, io_timeout: Optional[float] = None) -> List[Entry]:
    #     return self.find_all(name, filter, Direction.RECV, io_timeout)

    # def find_all_sent(self, name: str, filter: Optional[lc.Filter] = None, io_timeout: Optional[float] = None) -> List[Entry]:
    #     return self.find_all(name, filter, Direction.RECV, io_timeout)


class MemoryStoreCallback(Store, lc.Chainable):
    def __init__(self, io_timeout: Optional[float] = 1.0):
        super().__init__()
        self.__store: List[Entry] = []
        self.__io_timeout = io_timeout

    def on_recv(self, con_id: ConId, msg: Message) -> None:
        self.__store.append(Entry(Direction.RECV, datetime.now(), con_id, msg))
        super().on_recv(con_id, msg)

    def on_sent(self, con_id: ConId, msg: Message) -> None:
        self.__store.append(Entry(Direction.SENT, datetime.now(), con_id, msg))
        super().on_sent(con_id, msg)

    @property
    def reversed_store(self) -> Iterator[Entry]:
        return reversed(self.__store)

    @property
    def io_timeout(self) -> Optional[float]:
        return self.__io_timeout

    # @property
    @io_timeout.setter
    def io_timeout(self, io_timeout: float) -> None:
        self.__io_timeout = io_timeout

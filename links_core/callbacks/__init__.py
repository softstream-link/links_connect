from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


class ConType(Enum):
    Initiator = auto()
    Acceptor = auto()


MsgDict = dict[str, str | int | float | bool | dict | list]  # Any?


@dataclass
class ConId:
    con_type: ConType = ConType.Initiator
    name: str = "unknown"
    local: str = "unknown"
    peer: str =  "unknown"


class Callback(ABC):
    @abstractmethod
    def on_recv(self, con_id: ConId, msg: MsgDict) -> None:
        ...

    @abstractmethod
    def on_sent(self, con_id: ConId, msg: MsgDict) -> None:
        ...





# https://stackoverflow.com/questions/11731136/class-method-decorator-with-self-arguments


def match(attr, func) -> None:
    def decorator(func):
        return func()

    return decorator(func)

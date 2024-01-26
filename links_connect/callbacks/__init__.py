from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict


class ConType(Enum):
    Initiator = auto()
    Acceptor = auto()


@dataclass
class ConId:
    con_type: ConType = ConType.Initiator
    name: str = "unknown"
    local: str = "unknown"
    peer: str = "unknown"


Message = Dict
Filter = Dict


class Callback(metaclass=ABCMeta):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_recv(self, con_id: ConId, msg: Message) -> None:
        return

    @abstractmethod
    def on_sent(self, con_id: ConId, msg: Message) -> None:
        return

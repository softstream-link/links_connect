import abc
import dataclasses
import enum
import typing


class ConType(enum.Enum):
    Initiator = enum.auto()
    Acceptor = enum.auto()

    def __str__(self) -> str:
        if self == ConType.Initiator:
            return "Initiator"
        else:
            return "Acceptor"


@dataclasses.dataclass
class ConId:
    con_type: ConType = ConType.Initiator
    name: str = "unknown"
    local: str = "unknown"
    peer: str = "unknown"

    def __str__(self) -> str:
        # Initiator(clt-ouch@127.0.0.1:53036->127.0.0.1:8080)
        return f"{self.con_type}({self.name}@{self.local}->{self.peer})"


Message = typing.Dict
Filter = typing.Dict


class Callback(metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def on_recv(self, con_id: ConId, msg: Message) -> None:
        ...

    @abc.abstractmethod
    def on_sent(self, con_id: ConId, msg: Message) -> None:
        ...


def is_matching(filter: Filter, msg: Message) -> bool:
    for f_key, f_val in filter.items():
        match msg.get(f_key, None):
            case None:
                return True if f_val is None else False
            case dict() as d_val:
                if (not isinstance(f_val, dict)) or (
                    isinstance(f_val, dict)
                    and len(f_val) != 0
                    and not is_matching(f_val, d_val)
                ):
                    return False
            case _ as d_val:
                if f_val != d_val:
                    return False

    return True

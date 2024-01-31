import logging
from links_connect.callbacks import ChainableCallback, ConId, Message
import typing


class LoggerCallback(ChainableCallback):
    def __init__(
        self,
        recv_level=logging.INFO,
        sent_level=logging.INFO,
        name: typing.Optional[str] = None,
    ) -> None:
        super().__init__()
        self.__recv_level = recv_level
        self.__sent_level = sent_level
        self.__name = name

    def on_sent(self, con_id: ConId, msg: Message) -> None:
        logging.getLogger(__name__).log(
            self.__sent_level,
            f"{self.name}.on_sent: {con_id} {type(msg).__name__}({msg})",
        )
        super().on_sent(con_id, msg)

    def on_recv(self, con_id: ConId, msg: Message) -> None:
        logging.getLogger(__name__).log(
            self.__recv_level,
            f"{self.name}.on_recv: {con_id} {type(msg).__name__}({msg})",
        )
        super().on_recv(con_id, msg)

    @property
    def name(self) -> str:
        return f"{self.__class__.__name__ if self.__name is None else self.__name}"

    def __str__(self) -> str:
        return f"{self.name}, recv_level={self.__recv_level}, sent_level={self.__sent_level}"

import logging
from links_connect.callbacks import Callback, ConId, Message

class LoggerCallback(Callback):
    def __init__(self, sent_level=logging.INFO, recv_level=logging.INFO) -> None:
        super().__init__()
        self.sent_level = sent_level
        self.recv_level = recv_level

    def on_sent(self, con_id: ConId, msg: Message):
        logging.getLogger(__name__).log(self.sent_level, f"{self.__class__.__name__}.on_sent: {con_id} {type(msg).__name__}({msg})")

    def on_recv(self, con_id: ConId, msg: Message):
        logging.getLogger(__name__).log(self.recv_level, f"{self.__class__.__name__}.on_recv: {con_id} {type(msg).__name__}({msg})")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}, sent_level={self.sent_level}, recv_level={self.recv_level}"
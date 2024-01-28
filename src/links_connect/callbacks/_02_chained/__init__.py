import links_connect.callbacks._01_core as _01_core
from typing import List


class ChainableCallback(_01_core.Callback):
    def __init__(self):
        super().__init__()
        self.__callback_chain: List[_01_core.Callback] = []

    def on_recv(self, con_id: _01_core.ConId, msg: _01_core.Message) -> None:
        for callback in self.__callback_chain:
            callback.on_recv(con_id, msg)

    def on_sent(self, con_id: _01_core.ConId, msg: _01_core.Message) -> None:
        for callback in self.__callback_chain:
            callback.on_sent(con_id, msg)

    def __add__(self, other: _01_core.Callback):
        self.__callback_chain.append(other)
        return self

import links_connect as lc
from typing import List


class Chainable(lc.Callback):
    def __init__(self):
        super().__init__()
        self.__callbacks: List[lc.Callback] = []

    def on_recv(self, con_id: lc.ConId, msg: lc.Message) -> None:
        for callback in self.__callbacks:
            callback.on_recv(con_id, msg)

    def on_sent(self, con_id: lc.ConId, msg: lc.Message) -> None:
        for callback in self.__callbacks:
            callback.on_sent(con_id, msg)

    def __add__(self, other: lc.Callback):
        self.__callbacks.append(other)
        return self

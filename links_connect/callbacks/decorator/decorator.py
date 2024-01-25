from links_connect.callbacks import ConId, Message, Filter
from links_connect.callbacks.decorator import CallbackRegistry, DecoratorBase, CallbackFunction


import logging


log = logging.getLogger(__name__)


class Sender:
    def send(self, msg: dict, io_timeout: float | None = None):
        raise Exception(f"{self.__class__.__name__}.send: Not Implemented")

    def is_connected(self, io_timeout: float | None = None) -> bool:
        raise Exception(f"{self.__class__.__name__}.is_connected: Not Implemented")

    def __str__(self) -> str:
        return f"{self.__class__.__name__} Not Implemented"


class SettableSender:
    def __init__(self) -> None:
        self._sender = Sender()

    @property
    def sender(self) -> Sender:
        return self._sender

    @sender.setter
    def sender(self, sender: Sender):
        self._sender = sender


class DecoratorDriver(DecoratorBase, SettableSender):
    def __init__(self, sent_level=logging.INFO, recv_level=logging.INFO) -> None:
        super().__init__()
        self._sent_level = sent_level
        self._recv_level = recv_level

    def on_sent(self, con_id: ConId, msg: Message):
        registry = CallbackRegistry.get(self.__class__.__name__).on_sent_filter_callback_entries
        match registry.find(msg):
            case None:
                log.debug(f"{self.__class__.__name__}.on_sent: Callback Not Registered {con_id} {type(msg).__name__}({msg})")
            case function:
                log.log(self._sent_level, f"{self.__class__.__name__}.on_sent: {function} {con_id} {type(msg).__name__}({msg})")
                function(self, con_id, msg)

    def on_recv(self, con_id: ConId, msg: Message):
        registry = CallbackRegistry.get(self.__class__.__name__).on_recv_filter_callback_entries
        match registry.find(msg):
            case None:
                log.warning(f"{self.__class__.__name__}.on_recv: Callback Not Registered {con_id} {type(msg).__name__}({msg})")
            case function:
                log.log(self._recv_level, f"{self.__class__.__name__}.on_recv: {function} {con_id} {type(msg).__name__}({msg})")
                function(self, con_id, msg)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{'sender': {self.sender}}}\n{CallbackRegistry.get(self.__class__.__name__)}"

from typing import Callable, Any, Type


def on_recv(filter: Filter, scope: str):
    def decorator(function: Callable[[Any, ConId, Message], None]):
        filter_callback_entries = CallbackRegistry.get(scope).on_recv_filter_callback_entries
        existing_function = filter_callback_entries.get(filter)
        if existing_function is None:
            filter_callback_entries.push(filter, function)
        else:
            raise Exception(
                f"@on_recv: attempting to register filter: {filter} with function: {function} but function: {existing_function} already registered against this filter"
            )

        return function

    return decorator


def on_sent(filter: Filter, scope: str):
    def decorator(function: Callable[[Any, ConId, Message], None]):
        filter_callback_entries = CallbackRegistry.get(scope).on_sent_filter_callback_entries
        existing_function = filter_callback_entries.get(filter)
        if existing_function is None:
            filter_callback_entries.push(filter, function)
        else:
            raise Exception(
                f"@on_sent: attempting to register filter: {filter} with function: {function} but function: {existing_function} already registered against this filter"
            )

        return function

    return decorator

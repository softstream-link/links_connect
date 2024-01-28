import links_connect as lc
from links_connect.callbacks.decorator.registry import CallbackRegistry, DecoratorDriverBase, CallbackFunction
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
    def __init__(self):
        super().__init__()
        self.__sender = Sender()

    @property
    def sender(self) -> Sender:
        return self.__sender

    @sender.setter
    def sender(self, sender: Sender):
        self.__sender = sender


class DecoratorDriver(DecoratorDriverBase, SettableSender):
    def __init__(self) -> None:
        super().__init__()

    def on_sent(self, con_id: lc.ConId, msg: lc.Message) -> None:
        registry = CallbackRegistry.get(self.__class__.__name__).on_sent_filter_callback_entries
        match registry.find(msg):
            case None:
                log.warning(
                    f"{DecoratorDriver.__name__}.on_sent of instance {self.__class__.__name__} no registered delegate function {con_id} {type(msg).__name__}({msg})"
                )
            case function:
                log.debug(f"{DecoratorDriver.__name__}.on_sent of instance {self.__class__.__name__} delegating to registered {function}")
                function(self, con_id, msg)
        super().on_sent(con_id, msg)

    def on_recv(self, con_id: lc.ConId, msg: lc.Message) -> None:
        registry = CallbackRegistry.get(self.__class__.__name__).on_recv_filter_callback_entries
        match registry.find(msg):
            case None:
                log.warning(
                    f"{DecoratorDriver.__name__}.on_recv of instance {self.__class__.__name__} no registered delegate function {con_id} {type(msg).__name__}({msg})"
                )
            case function:
                log.debug(f"{DecoratorDriver.__name__}.on_recv of instance {self.__class__.__name__} delegating to registered {function}")
                function(self, con_id, msg)
        super().on_recv(con_id, msg)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{'sender': {self.sender}}}\n{CallbackRegistry.get(self.__class__.__name__)}"


from typing import Callable, Any, Type


def on_recv(filter: lc.Filter, scope: str):
    def decorator(function: Callable[[Any, lc.ConId, lc.Message], None]):
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


def on_sent(filter: lc.Filter, scope: str):
    def decorator(function: Callable[[Any, lc.ConId, lc.Message], None]):
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

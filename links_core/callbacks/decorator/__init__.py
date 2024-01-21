from links_core.callbacks import Callback, ConId, MsgDict
from links_core.callbacks.decorator.registry import CallbackRegistry, Filter
import logging

log = logging.getLogger(__name__)


class Registry:
    _registry_on_recv = CallbackRegistry()
    _registry_on_sent = CallbackRegistry()

    @classmethod
    @property
    def registry_on_recv(cls) -> CallbackRegistry:
        return cls._registry_on_recv

    @classmethod
    @property
    def registry_on_sent(cls) -> CallbackRegistry:
        return cls._registry_on_sent

    def __str__(self) -> str:
        return f"\non_recv:" + f"{self.registry_on_recv}" + f"\non_sent:" + f"{self.registry_on_sent}"


class Sender:
    def send(self, msg: dict, io_timeout: float | None = None):
        ...

    def is_connected(self, io_timeout: float | None = None) -> bool:
        ...


class ScenarioCallbackDriver(Callback, Registry):
    def __init__(self):
        self._sender: Sender | None = None

    def on_sent(self, con_id: ConId, msg: MsgDict):
        match self.registry_on_sent.find(msg):
            case None:
                if log.isEnabledFor(logging.WARNING):
                    log.warning(f"{self.__class__.__name__}.on_sent: Callback Not Registered {con_id} {type(msg).__name__}({msg})")
            case entry:
                entry.function(self, con_id, msg)

    def on_recv(self, con_id: ConId, msg: MsgDict):
        match self.registry_on_recv.find(msg):
            case None:
                if log.isEnabledFor(logging.WARNING):
                    log.warning(f"{self.__class__.__name__}.on_recv: Callback Not Registered {con_id} {type(msg).__name__}({msg})")
            case entry:
                entry.function(self, con_id, msg)

    @property
    def sender(self) -> Sender | None:
        self._sender

    @sender.setter
    def sender(self, sender: Sender):
        self._sender = sender

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{{'sender': {self.sender}}}" + Registry.__str__(self)


def on_recv(filter: Filter, registry: Registry):
    def decorator(function: callable):
        existing_function = registry.registry_on_recv.get(filter)
        if existing_function is None:
            registry.registry_on_recv.push(filter, function)
        else:
            raise Exception(
                f"@on_recv: attempting to register filter: {filter} with function: {function} but function: {existing_function} already registered against this filter"
            )

        return function

    return decorator


def on_sent(filter: Filter, registry: Registry):
    def decorator(function: callable):
        existing_function = registry.registry_on_sent.get(filter)
        if existing_function is None:
            registry.registry_on_sent.push(filter, function)
        else:
            raise Exception(
                f"@on_sent: attempting to register filter: {filter} with function: {function} but function: {existing_function} already registered against this filter"
            )

        return function

    return decorator

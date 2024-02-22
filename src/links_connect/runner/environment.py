from typing import Dict, Callable, Any, List, Concatenate, Optional, Sequence
from links_connect.callbacks import Message, Callback, MemoryStoreCallback, Direction, Filter
from dataclasses import dataclass
import logging

log = logging.getLogger(__name__)

Address = str
Name = str

Constructor = Callable[Concatenate[Address, Callback, ...], Any]


@dataclass
class LinkConfig:
    name: Name
    impl: Constructor
    addr: Address
    settings: Dict


class RunnerConfig:
    def __init__(
        self,
        link_configs: List[LinkConfig],
        default_io_timeout: Optional[float] = None,
        activate_on_init: Optional[bool] = True,
        log_also_console: Optional[bool] = False,
    ) -> None:
        self.__link_configs: Dict[Name, LinkConfig] = {config.name: config for config in link_configs}
        self.__default_io_timeout = default_io_timeout
        self.__start_on_init = activate_on_init
        self.__log_also_console = log_also_console

    def get_link_configs(self, name: Optional[Name] = None) -> Sequence[LinkConfig]:
        """
        Returns a sequence of LinkConfig objects.

        Arguments:
            name: Optional[Name] = None - when None, it returns all LinkConfig objects as sequence
            , otherwise it returns only the LinkConfig object with the given name as a sequence of one element.
        """
        if name is not None:
            assert name in self.__link_configs.keys(), f"LinkNameInvalidError: name: '{name}'. Valid names are: {self.__link_configs.keys()}"
            return [self.__link_configs[name]]
        else:
            return list(self.__link_configs.values())

    @property
    def default_io_timeout(self) -> Optional[float]:
        return self.__default_io_timeout

    @property
    def start_on_init(self) -> bool:
        return self.__start_on_init  # type: ignore

    @property
    def log_also_console(self) -> bool:
        return self.__log_also_console  # type: ignore


class Link:
    def __init__(self, config: LinkConfig, store_callback: MemoryStoreCallback):
        self.__config = config
        self.__store_callback = store_callback
        self.__instance = self.__config.impl(
            self.__config.addr,
            self.__store_callback,
            **self.__config.settings,
        )

    def send(self, message: Message, io_timeout: Optional[float] = None):
        self.__instance.send(message, io_timeout)

    def recv(self, filter: Optional[Filter] = None, io_timeout: Optional[float] = None) -> Message:
        entry = self.__store_callback.find_recv(name=self.__config.name, filter=filter, find_timeout=io_timeout)
        assert (
            entry is not None
        ), f"FailedRecvError: io_timeout: {io_timeout}, filter: {filter}, state: {self.__store_callback.state(name=self.__config.name, direction=Direction.RECV)}"

        return entry.msg

    def is_connected(self, io_timeout: Optional[float] = None) -> bool:
        return self.__instance.is_connected(io_timeout)

    def shutdown(self):
        self.__instance.__exit__(None, None, None)

    def __str__(self) -> str:
        return f"'{self.__config.name}': {self.__instance}"


class Runner:
    def __init__(self, default_recv_timeout: Optional[float]) -> None:
        self.__link_instances: Dict[Name, Link] = {}
        self.__memory_store = MemoryStoreCallback(default_find_timeout=default_recv_timeout)

    def start(self, config: LinkConfig):
        assert config.name not in self.__link_instances.keys(), f"LinkStateInvalidError: Link '{config.name}' already Started"
        link = Link(config, self.__memory_store)
        self.__link_instances[config.name] = link
        if log.isEnabledFor(logging.INFO):
            log.info(f"Started link: {link}")

    def stop(self, name: Name):
        link = self._pop_valid_link(name)
        link.shutdown()
        if log.isEnabledFor(logging.INFO):
            log.info(f"Stopped link: {link}")

    def _validate_link_name(self, name: Name) -> None:
        assert (
            name in self.__link_instances.keys()
        ), f"LinkStateInvalidError: name: '{name}' is not running or valid. Running link names are: {self.__link_instances.keys()}"

    def _get_valid_link(self, name: Name) -> Link:
        self._validate_link_name(name)
        return self.__link_instances[name]

    def _pop_valid_link(self, name: Name) -> Link:
        self._validate_link_name(name)
        return self.__link_instances.pop(name)

    def send(self, name: Name, message: Message, io_timeout: Optional[float] = None):
        link = self._get_valid_link(name)
        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"Sending name: '{name}', io_timeout: {io_timeout}, link: {link}, message: {message}")
        link.send(message, io_timeout)

    def recv(self, name: Name, filter: Optional[Filter] = None, io_timeout: Optional[float] = None) -> Message:
        link = self._get_valid_link(name)
        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"Receiving name: '{name}', io_timeout: {io_timeout}")
        return link.recv(filter, io_timeout)

    def is_connected(self, name: Name, io_timeout: Optional[float] = None) -> bool:
        link = self._get_valid_link(name)
        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"Is connected name: '{name}', link: {link}")
        return link.is_connected(io_timeout)

    def state(self, name: Optional[Name] = None, direction: Optional[Direction] = None) -> str:
        return self.__memory_store.state(name, direction)

    def clear_recved(self, name: Optional[Name] = None):
        self.__memory_store.clear(name)

    def __str__(self) -> str:
        return f"Runner links: #{len(self.__link_instances):,}\n: {'\n'.join([str(link) for link in self.__link_instances.values()])}"

    def __repr__(self) -> str:
        return f"Runner state: #{len(self.__link_instances):,}\n{self.__memory_store.state()}"

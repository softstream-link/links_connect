from typing import Dict, Callable, Self,  Any, List, Sequence, Concatenate, Optional
from links_connect.callbacks import Message, Callback
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


class Link:
    def __init__(self, config: LinkConfig, callback: Callback):
        self.config = config
        self.__instance = config.impl(config.addr, callback, **config.settings)

    def send(self, message: Message, io_timeout: Optional[float] = None):
        self.__instance.send(message, io_timeout)

    def is_connected(self) -> bool:
        return self.__instance.is_connected()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__instance.__exit__(exc_type, exc_value, traceback)

    def __str__(self) -> str:
        return f"{self.__instance}"


class RunnerConfig:
    def __init__(self, config: List[LinkConfig], io_timeout: Optional[float] = None, log_also_console: bool = False) -> None:
        self.__links_global = config
        self.__io_timeout = io_timeout
        self.__log_also_console = log_also_console


    @property
    def links_global(self) -> Sequence[LinkConfig]:
        return self.__links_global
    
    @property
    def io_timeout(self) -> Optional[float]:
        return self.__io_timeout
    
    @property
    def log_also_console(self) -> bool:
        return self.__log_also_console


class Runner:
    def __init__(self) -> None:
        self.__links_instances: Dict[Name, Link] = {}
    
    def get_link(self, name: Name) -> Link:
        link = self.__links_instances.get(name)
        assert link is not None , f"name: '{name}' is not valid. Valid names are: {self.__links_instances.keys()}"
        return link

    def add_link(self, link: Link):
        self.__links_instances[link.config.name] = link
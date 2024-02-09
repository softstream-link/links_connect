from typing import Dict, Callable, Self,  Any, List, Sequence, Concatenate
from links_connect.callbacks import Message, Callback
from dataclasses import dataclass

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

    def send(self, message: Message):
        self.__instance.send(message)

    def is_connected(self) -> bool:
        return self.__instance.is_connected()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__instance.__exit__(exc_type, exc_value, traceback)


class RunnerConfig:
    def __init__(self, config: List[LinkConfig]) -> None:
        self.__links_global = config


    @property
    def links_global(self) -> Sequence[LinkConfig]:
        return self.__links_global


class Runner:
    def __init__(self) -> None:
        self.__links_instances: Dict[Name, Link] = {}
    
    def get_link(self, name: Name) -> Link:
        link = self.__links_instances.get(name)
        assert link is not None , f"name: '{name}' is not valid. Valid names are: {self.__links_instances.keys()}"
        return link

    def add_link(self, link: Link):
        self.__links_instances[link.config.name] = link
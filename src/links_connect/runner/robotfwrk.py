from robot.api.deco import library, keyword
from links_connect.runner.environment import RunnerConfig, Runner, Link
from links_connect.callbacks import MemoryStoreCallback, Message, Filter
from typing import Optional


@library(scope="GLOBAL")
class LinksRobotRunner:

    def __init__(self, runner_config: RunnerConfig) -> None:
        super().__init__()
        self.__runner = Runner()
        self.__memory_store = MemoryStoreCallback()
        for config in runner_config.links_global:
            link = Link(config, self.__memory_store)
            self.__runner.add_link(link)

    @keyword
    def send(self, name: str, message: Message):
        link = self.__runner.get_link(name)
        link.send(message)

    def recv(self, name: str, filter: Filter) -> Optional[Message]:
        entry = self.__memory_store.find_recv(name=name, filter=filter)
        return None if entry is None else entry.msg
            
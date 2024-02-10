from robot.api.deco import library, keyword
from robot.api import logger
from links_connect.runner.environment import RunnerConfig, Runner, Link
from links_connect.callbacks import MemoryStoreCallback, Message, Filter, Direction
from typing import Optional

# import logging
# log = logging.getLogger(__name__)
# from robotbackgroundlogger import BackgroundLogger
# logger = BackgroundLogger()
log = logger





@library(scope="GLOBAL")
class LinksRobotRunner:

    def __init__(self, runner_config: RunnerConfig) -> None:
        super().__init__()
        self.__runner_config = runner_config
        self.__runner = Runner()
        self.__memory_store = MemoryStoreCallback(self.__runner_config.io_timeout)

        for config in self.__runner_config.links_global:
            link = Link(config, self.__memory_store)
            log.info(f"created link:{link}")
            self.__runner.add_link(link)

    @keyword("Link ${name} Send Message ${message} with timeout ${io_timeout}")
    def send_with_io_timeout(self, name: str, message: Message, io_timeout: Optional[float] = None):
        link = self.__runner.get_link(name)
        log.info(f"Send link: {link}, io_timeout: {io_timeout}, message: {message}")
        link.send(message=message, io_timeout=io_timeout if io_timeout is not None else self.__runner_config.io_timeout)

    @keyword("Link ${name} Send Message ${message}")
    def send_with_default_io_timeout(self, name: str, message: Message):
        self.send_with_io_timeout(name, message, self.__runner_config.io_timeout)

    @keyword("Link ${name} Recv Filter ${filter} with timeout ${io_timeout}")
    def recv_with_io_timeout(self, name: str, filter: Filter, io_timeout: Optional[float] = None) -> Message:
        entry = self.__memory_store.find_recv(name=name, filter=filter, io_timeout=io_timeout)
        if entry is None:
            class FailedToFindMatchingMessage(Exception):
                def __init__(self, *args: object) -> None:
                    super().__init__(*args)
            raise FailedToFindMatchingMessage(f"io_timeout: {io_timeout}, filter: {filter}, state: {self.__memory_store.state_2_str(name=name, direction=Direction.RECV)}")
        else:
            link = self.__runner.get_link(name)
            io_timeout = self.__memory_store.effective_timeout(io_timeout)
            log.info(f"Recv link: {link}, io_timeout: {io_timeout}, filter: {filter}, message: {entry.msg}")
            return entry.msg

    @keyword("Link ${name} Recv Filter ${filter}")
    def recv_with_default_io_timeout(self, name: str, filter: Filter) -> Message:
        return self.recv_with_io_timeout(name, filter, self.__runner_config.io_timeout)

    @keyword("Link All Log State")
    def log_all_state(self):
        log.info(f"\n{self.__memory_store.state_2_str(name=None)}", also_console=self.__runner_config.log_also_console)

    @keyword("Link ${name} Log State")
    def log_state(self, name: str):
        log.info(f"\n{self.__memory_store.state_2_str(name=name)}", also_console=True)
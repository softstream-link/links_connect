from robot.api.deco import library, keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from links_connect.runner.environment import RunnerConfig, Runner, Link, Name
from links_connect.callbacks import MemoryStoreCallback, Message, Filter, Direction
from typing import Optional, List, Final
from time import sleep

# import logging
# log = logging.getLogger(__name__)
# from robotbackgroundlogger import BackgroundLogger
# logger = BackgroundLogger()
log = logger
YIELD_DURATION: Final[float] = 1.0


@library(scope="GLOBAL", auto_keywords=False, version="0.1")  # TODO read version from lib's metadata
class LinksRobotRunner:

    def __init__(self, runner_config: Optional[RunnerConfig] = None) -> None:
        super().__init__()

        if not BuiltIn().robot_running:
            return
        assert runner_config is not None, "RunnerConfigError: RunnerConfig is required"

        self.__runner_config = runner_config
        self.__runner = Runner(default_recv_timeout=self.__runner_config.default_io_timeout)

        if self.__runner_config.start_on_init:
            self.start()
        else:
            log.info(
                f"Links not started start_on_init: {self.__runner_config.start_on_init}\n{'\n'.join(str(config) for config in self.__runner_config.get_link_configs())}",
                also_console=self.__runner_config.log_also_console,
            )

    def effective_timeout(self, io_timeout: Optional[float]) -> float:
        if io_timeout is not None:
            return io_timeout
        elif self.__runner_config.default_io_timeout is not None:
            return self.__runner_config.default_io_timeout
        else:
            return 0.0

    @keyword("Link All Start")
    def start(self, name: Optional[Name] = None):
        for config in self.__runner_config.get_link_configs(name):
            log.info(f"Starting config: {config}", also_console=self.__runner_config.log_also_console)
            self.__runner.start(config)

    @keyword("Link ${name} Start")
    def start_name(self, name: str):
        self.start(name)

    @keyword("Link All Stop")
    def stop(self, name: Optional[str] = None):
        for config in self.__runner_config.get_link_configs(name):
            log.info(f"Stopping config: {config}", also_console=self.__runner_config.log_also_console)
            self.__runner.stop(config.name)

    @keyword("Link ${name} Stop")
    def stop_name(self, name: str):
        self.stop(name)

    @keyword("Link ${name} Send Message ${message}")
    def send(self, name: str, message: Message):
        io_timeout = self.effective_timeout(None)
        log.info(f"Sending name: '{name}', message: {message}, io_timeout: {io_timeout}", also_console=self.__runner_config.log_also_console)
        self.__runner.send(name, message, io_timeout)

    @keyword("Link ${name} Send Message ${message} with timeout ${io_timeout}")
    def send_io_timeout(self, name: str, message: Message, io_timeout: Optional[float] = None):
        io_timeout = self.effective_timeout(io_timeout)
        log.info(f"Sending name: '{name}', io_timeout: {io_timeout}, message: {message}", also_console=self.__runner_config.log_also_console)
        self.__runner.send(name, message, io_timeout)

    @keyword("Link All Clear Recved")
    def recv_clear_all(self):
        log.info(f"Clearing All Recv'ed", also_console=self.__runner_config.log_also_console)
        self.__runner.clear_recved()

    @keyword("Link ${name} Clear Recved")
    def recv_clear(self, name: str):
        log.info(f"Clearing name: {name} Recv'ed", also_console=self.__runner_config.log_also_console)
        self.__runner.clear_recved(name)

    @keyword("Link ${name} Recv Filter ${filter} with timeout ${io_timeout}")
    def recv_io_timeout(self, name: str, filter: Filter, io_timeout: Optional[float] = None) -> Message:
        io_timeout = self.effective_timeout(io_timeout)
        log.info(f"Receiving name: '{name}', io_timeout: {io_timeout}, filter: {filter}")
        return self.__runner.recv(name, filter, io_timeout)

    @keyword("Link ${name} Recv Filter ${filter}")
    def recv(self, name: str, filter: Filter) -> Message:
        io_timeout = self.effective_timeout(None)
        log.info(f"Receiving name: '{name}', io_timeout: {io_timeout}, filter: {filter}")
        return self.recv_io_timeout(name, filter, io_timeout)

    @keyword("Link All Should be Connected")
    def all_should_be_connected(self, name: Optional[Name] = None, io_timeout: Optional[float] = None):
        status: List[str] = []
        disconnected_count: int = 0

        configs = self.__runner_config.get_link_configs(name)
        effective_timeout = self.effective_timeout(io_timeout)

        for config in configs:
            is_connected = self.__runner.is_connected(config.name, effective_timeout)
            status.append(f"Connected name: '{config.name}'" if is_connected else f"Disconnected name: '{config.name}'")
            disconnected_count += 0 if is_connected else 1

        assert (
            disconnected_count == 0
        ), f"LinkDisconnectedError: {disconnected_count:,} of {len(configs):,} Disconnected. io_timeout: {effective_timeout}\n{'\n'.join(status)}"

        log.info(
            f"All {len(configs):,} Connected. io_timeout: {effective_timeout}\n{'\n'.join(status)}",
            also_console=self.__runner_config.log_also_console,
        )

    @keyword("Link All Should be Connected with timeout: ${io_timeout}")
    def all_should_be_connected_io_timeout(self, io_timeout: float):
        self.all_should_be_connected(io_timeout=io_timeout)

    @keyword("Link ${name} Should be Connected")
    def name_should_be_connected(self, name: str):
        self.all_should_be_connected(name=name)

    @keyword("Link ${name} Should be Connected with timeout: ${io_timeout}")
    def name_connected_with_timeout(self, name: str, io_timeout: float):
        self.all_should_be_connected(name=name, io_timeout=io_timeout)

    @keyword("Link All Should Not be Connected")
    def all_should_not_be_connected(self, name: Optional[str] = None, io_timeout: Optional[float] = 0.0):
        status: List[str] = []
        connected_count: int = 0

        configs = self.__runner_config.get_link_configs(name)
        effective_timeout = self.effective_timeout(io_timeout)

        for config in configs:
            is_connected = self.__runner.is_connected(config.name, io_timeout=effective_timeout)  # important to pas io_timeout to 0
            status.append(f"Connected name: '{config.name}'" if is_connected else f"Disconnected name: '{config.name}'")
            connected_count += 1 if is_connected else 0

        assert (
            connected_count == 0
        ), f"LinkConnectedError: {connected_count:,} of {len(configs):,} Connected. io_timeout: {effective_timeout}\n{'\n'.join(status)}"
        log.info(
            f"All {len(configs):,} Disconnected. io_timeout: {effective_timeout}\n{'\n'.join(status)}",
            also_console=self.__runner_config.log_also_console,
        )

    @keyword("Link ${name} Should Not be Connected")
    def name_should_not_be_connected(self, name: str):
        self.all_should_not_be_connected(name=name)

    @keyword("Link All Log State")
    def all_log_state(self, name: Optional[str] = None):
        log.info(f"{self.__runner.state(name=name)}", also_console=self.__runner_config.log_also_console)

    @keyword("Link ${name} Log State")
    def name_log_state(self, name: str):
        self.all_log_state(name=name)

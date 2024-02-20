from links_connect.runner.environment import RunnerConfig, Link, LinkConfig, Runner
from links_connect.callbacks import MemoryStoreCallback


class NativeRunner:
    def __init__(self, runner_config: RunnerConfig) -> None:
        super().__init__()
        self.runner = Runner()
        callback = MemoryStoreCallback()
        for config in runner_config.link_configs:
            link = Link(config, callback)
            self.runner.add_link(link)


    

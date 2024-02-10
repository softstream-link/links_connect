from links_connect.runner import RunnerConfig, LinkConfig
from ouch_connect import SvcAuto, CltManual


# from robot.api import logger
# from logging import Logger
# import logging
# Logger.info = lambda msg: logger.info(msg, also_console=True)
# logging.basicConfig(level=logging.INFO)

def get_variables() -> dict:
    clt = "clt-ouch"
    svc = "svc-ouch"
    io_timeout = 0.5
    config = RunnerConfig(
        [
            LinkConfig(svc, SvcAuto, "127.0.0.1:8080", {"name": svc}),
            LinkConfig(clt, CltManual, "127.0.0.1:8080", {"name": clt}),
        ],
        io_timeout=io_timeout,
        log_also_console=True,
    )
    return {
        "RUNNER_CONFIG": config,
        "clt": clt,
        "svc": svc,
    }

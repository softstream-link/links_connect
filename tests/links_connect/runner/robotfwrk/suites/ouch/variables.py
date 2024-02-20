import sys

sys.path.append("./../ouch/bindings/python")

from links_connect.runner import RunnerConfig, LinkConfig
from ouch_connect import SvcAuto, CltManual
from robot.libraries.BuiltIn import BuiltIn


def get_variables() -> dict:
    clt = "clt-ouch"
    svc = "svc-ouch"
    io_timeout = 0.5
    config = RunnerConfig(
        [
            LinkConfig(svc, SvcAuto, "127.0.0.1:8080", dict(name=svc, io_timeout=io_timeout)),
            LinkConfig(clt, CltManual, "127.0.0.1:8080", dict(name=clt, io_timeout=io_timeout)),
        ],
        default_io_timeout=io_timeout,
        activate_on_init=False,
        log_also_console=True,
    )
    return {
        "RUNNER_CONFIG": config if BuiltIn().robot_running else "ROBOT NOT RUNNING",
        "clt": clt,
        "svc": svc,
    }

from links_connect.runner import RunnerConfig, LinkConfig
from ouch_connect import SvcAuto, CltManual


def get_variables():
    clt = "clt-ouch"
    svc = "svc-ouch"
    config = RunnerConfig(
        [
            LinkConfig(svc, SvcAuto, "127.0.0.1:8080", {}),
            LinkConfig(clt, CltManual, "127.0.0.1:8080", {}),
        ]
    )
    return {
        "RUNNER_CONFIG": config,
        "clt": clt,
        "svc": svc,
    }

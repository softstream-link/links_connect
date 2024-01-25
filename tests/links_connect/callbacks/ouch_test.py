# from links_connect import ConId, Message, DecoratorDriver, on_recv, LoggerCallback
# from ouch_connect import CltManual, SvcManual
# import logging
# from time import sleep
# from typing import Self

# log = logging.getLogger(__name__)
# host = "127.0.0.1:8081"


# class SvcLoginSimulator(DecoratorDriver):
#     def __init__(self, io_timeout: float = 0.5):
#         super().__init__(sent_level=logging.DEBUG, recv_level=logging.INFO)
#         self._io_timeout = io_timeout

#     @on_recv(filter={"LoginRequest": {}}, registry=DecoratorDriver)
#     def login_request(self, con_id: ConId, msg: Message):
#         self.sender.send({"LoginAccepted": {"session_id": "session #1", "sequence_number": "1"}})

#     @on_recv(filter={"HBeat": {}}, registry=DecoratorDriver)
#     def hbeat(self, con_id: ConId, msg: Message):
#         self.sender.send({"HBeat": {}})


# def test_ouch():
#     svc_clbk = SvcLoginSimulator()

#     svc = SvcManual(host, svc_clbk, name="svc")
#     clt = CltManual(host, LoggerCallback(), name="clt")

#     assert svc.is_connected()
#     assert clt.is_connected()
#     log.info(f"svc: {svc}")
#     log.info(f"clt: {clt}")

#     clt.send({"LoginRequest": {"username": "dummy", "password": "dummy", "session_id": "session #1", "sequence_number": "1"}})
#     clt.send({"HBeat": {}})
#     sleep(1)
#     log.info(f"***************** waited for hbeat *****************")


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] (%(threadName)10s) %(message)s (%(filename)s:%(lineno)s)")
#     test_ouch()
#     # import pytest
#     # pytest.main([__file__])

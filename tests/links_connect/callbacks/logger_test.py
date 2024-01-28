import pytest
from unittest.mock import Mock
from typing import Tuple
import logging

log = logging.getLogger(__name__)

@pytest.fixture
def mock_chained(mocker) -> Tuple[Mock, Mock]:
    from links_connect.callbacks import ChainableCallback
    original_on_recv = ChainableCallback.on_recv
    original_on_sent = ChainableCallback.on_sent

    mock_on_recv =  mocker.patch("links_connect.callbacks.ChainableCallback.on_recv", autospec=True)
    mock_on_sent =  mocker.patch("links_connect.callbacks.ChainableCallback.on_sent", autospec=True)

    mock_on_recv.side_effect = original_on_recv
    mock_on_sent.side_effect = original_on_sent
    return (mock_on_recv, mock_on_sent)



def test_logger(mock_chained):
    from links_connect.callbacks import ConId, Message, ConType, LoggerCallback
    clbk = LoggerCallback(name="LoggerCallbackFirst") + LoggerCallback(name="LoggerCallbackSecond") 

    clbk.on_sent(ConId(con_type=ConType.Initiator), {"sent": {}})
    clbk.on_recv(ConId(con_type=ConType.Acceptor), {"recv": {}})
    
    mock_on_recv, mock_on_sent = mock_chained
    log.info(f"mock_on_recv: {mock_on_recv.call_count }")
    log.info(f"mock_on_sent: {mock_on_sent.call_count }")
    assert mock_on_recv.call_count == 2
    assert mock_on_recv.call_count == 2


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])

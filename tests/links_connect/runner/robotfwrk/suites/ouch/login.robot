*** Variables ***
# LOGIN_SDFS       ${{ {"LoginRequest": {"username": "dummy", "password": "dummy", "session_id": "session #1", "sequence_number": "1"}} }}

*** Test Cases ***
Test Login Handshake
    ${login}=    Evaluate    ${{ {"LoginRequest": {"username": "dummy", "password": "dummy", "session_id": "session #1", "sequence_number": "1"}} }}
    Log    ${{ {"LoginRequest": {"username": "dummy", "password": "dummy", "session_id": "session #1", "sequence_number": "1"}} }}    console=True
    # Log ${login_request}
    # links.send(${clt}, )
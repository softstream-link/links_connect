# *** Settings ***
# Resource    main.resource

*** Settings ***
Variables     variables.py
Library       links_connect.runner.robotfwrk.LinksRobotRunner    ${RUNNER_CONFIG}     AS     link    # robotcode: ignore

*** Variables ***
# LOGIN_SDFS       ${{ {"LoginRequest": {"username": "dummy", "password": "dummy", "session_id": "session #1", "sequence_number": "1"}} }}
# &{login}=    ${{ dict(LoginRequest= dict(username= "dummy", password= "dummy", session_id= "session #1", sequence_number= "1")) }}
&{details}=    username=dummy    password=dummy    session_id=session #1    sequence_number=1
&{login}=      LoginRequest=&{details}

*** Test Cases ***
Test Login Handshake
    Log   ${{"\n"}} 
    Log    ${login}    console=${True}
    # Log ${login_request}
    link.send        ${clt}        ${login}
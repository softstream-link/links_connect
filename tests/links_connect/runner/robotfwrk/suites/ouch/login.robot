*** Settings ***
Variables         variables.py
Library           links_connect.runner.LinksRobotRunner    ${RUNNER_CONFIG}

Test Setup        Do Test Setup
Test Teardown     Do Test Teardown

*** Variables ***
${login_ack}=    &{{ dict(LoginAccepted= {}) }} 
${login_rej}=    &{{ dict(LoginRejected= {}) }} 

*** Test Cases ***
Test Successfull Login
    Link ${clt} Should be Connected
    Link ${svc} Should Not be Connected

    Link ${clt} Send Message &{{ dict(LoginRequest= dict(username= "dummy", password= "dummy", session_id= "", sequence_number= "1")) }}
    Link ${clt} Recv Filter ${login_ack}
    Run Keyword And Expect Error    FailedRecvError:*    Link ${clt} Recv Filter ${login_rej}
    
    Link All Should be Connected

Test Failed Login
    Link ${clt} Should be Connected
    Link ${svc} Should Not be Connected
    
    Link ${clt} Send Message &{{ dict(LoginRequest= dict(username= "wrong", password= "dummy", session_id= "", sequence_number= "1")) }}
    Link ${clt} Recv Filter ${login_rej}
    Run Keyword And Expect Error    FailedRecvError:*    Link ${clt} Recv Filter ${login_ack}

    Run Keyword And Expect Error    LinkDisconnectedError:*    Link All Should be Connected

*** Keywords ***
Do Test Setup
    Link All Start

Do Test Teardown
    Link All Stop
    Link All Log State
    Link All Clear Store
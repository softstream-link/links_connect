*** Settings ***
Variables     variables.py
Library       links_connect.runner.robotfwrk.LinksRobotRunner    ${RUNNER_CONFIG}


*** Variables ***
${login_req}=    ${{ dict(LoginRequest= dict(username= "dummy", password= "dummy", session_id= "", sequence_number= "1")) }}
${login_ack}=    ${{ dict(LoginAccepted= {}) }} 
${login_rej}=    ${{ dict(LoginRejected= {}) }} 

*** Test Cases ***
Test Login Handshake
    Link ${clt} Send Message ${login_req}
    Link ${clt} Recv Filter ${login_ack}
    Link ${clt} Recv Filter ${login_rej}
    Link All Log State
    Link ${clt} Log State

 

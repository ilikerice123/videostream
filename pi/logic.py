import os, sys, time, json
import serial

import requests
import subprocess
import time

from timeloop import Timeloop
from datetime import timedelta

from state import States
import wifi_script as wifi
import bt_serial as bluetooth
import leds
import api

ID_FILE = 'poke.id'
poke_id = None

# polls and waits on poke_id
def wait():
    global poke_id
    while True:
        resp = api.poll_poke(poke_id)
        if(resp['status'] == api.CONNECTION_ERROR):
            return States.Wifi
        elif(resp['body']['poked'] == True):
            return States.Flash

# initializes the variable poke_id
def setup():
    global poke_id
    if(poke_id is not None):
        return States.Wait

    try:
        file = open(ID_FILE, mode='r')
        poke_id = file.read()
        file.close()
        return States.Wait
    except FileNotFoundError:
        print('pokeid is null')
        return new_id()

# returns the next state based on if new_id succeeds or not
def new_id():
    global poke_id
    res = api.request_new()
    if(res['status'] == api.CONNECTION_ERROR):
        return States.Wifi
    tentative_id = res['body']['id']

    res = api.wait_activation(tentative_id)
    if(res['status'] == api.CONNECTION_ERROR):
        return States.Wifi
    if(res['body']['active'] != True):
        return States.Setup #try again, some error must've occurred
    
    # success, now we can save the id
    poke_id = res['body']['id']
    os.remove(ID_FILE)
    file = open(ID_FILE, mode='w')
    file.write(poke_id)
    file.close()
    return States.Wait

state = States.Wifi
if(wifi.has_wifi()):
    state = States.Wait
next_state = state

while True:
    if(state is States.Wifi):
        print("transitioning to wifi")
        if(wifi.connect()):
            next_state = States.Setup
    elif(state is States.Setup):
        print("transitioning to setup")
        next_state = setup()

    elif(state is States.Wait):
        print("transitioning to wait")
        next_state = wait()
    else:
        print("transitioning to flash")
        leds.flash()
        next_state = States.Wait

    state = next_state

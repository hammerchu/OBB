#!/usr/bin/python
import os
import logging
from threading import Thread
import time
import asyncio
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
from navigate import Navigate
import navigate

from classes.navigate import Navigate
from classes.plan import Plan
from classes.call import Call

logging.basicConfig(level=logging.INFO)

'''
Control center of the robot

Receive hi-level commands from HUBS and execute them as actions

- Travel to specific station (e.g. T204) via all the mini-goals
- Report stuck if get lost -> process follow up action
- Monitor and process location based zone-functions
- 
- Engage pickupper, unlock corresponding compartment and optionally lock up again
- Engage dropper, unlock corresponding compartment and lock up again
'''
app = Flask(__name__, static_url_path="", static_folder="static")
app.config.from_object('config')
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
CORS(app)

STATUS_CHECK_FREQ = 10 # check status 10 times one min

nav = asyncio.run(Navigate._init_()) # Nav instance
plan = Plan() # Plan instance
call = Call('M', 60, 0) # Call and Streaming instance
call.run('https://onbotbot.daily.co/_test')

def ask_for_help():
    is_asking_help = False
    while True:
        if nav.is_navigating:
            logging.info('Nav code report: ', nav.nav_code)
            if nav.nav_code and nav.nav_code >= 6:
                # ask for help from HUBS
                call.send_message(f'HELP - nav.nav_code: {nav.nav_code}')
                is_asking_help = True
        time.sleep(60/STATUS_CHECK_FREQ)



@app.route('/goto', methods=['POST'])
def goto():
    '''
    Travel to target station
    '''
    print('/post_goto')


def bringup():
    '''
    Prepare all the necessary components
    '''
    #do all the bringup task here
    pass
    




if __name__ == '__main__':
    logging.info('\n\n          -----BRAIN-----\n\n')
    
    app.run(host='0.0.0.0', port=8000, debug=True)


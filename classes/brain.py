#!/usr/bin/python
import os
import logging
from threading import Thread
import time
import asyncio
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO

from bot.classes.navigate import Navigate
from bot.classes.plan import Plan
from bot.classes.call import Call

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

STATUS_CHECK_FREQ = 20 

nav = asyncio.run(Navigate._init_()) # Nav instance
plan = Plan() # Plan instance
call = Call('M', 60, 0) # Call and Streaming instance
call.run('https://onbotbot.daily.co/_test')

def track_nav():
    '''
    Running in a separate thread to check if bbot stuck
    '''
    is_asking_help = False
    while True:
        call.heart_beat() # Send heart beat

        if nav.is_navigating:
            logging.debug('Nav code: ', nav.nav_code)
            if not is_asking_help and nav.nav_code and nav.nav_code >= 6:
                '''ask for help from HUBS'''
                logging.info('Stuck: ', nav.nav_code)
                call.stuck_message(nav.nav_code)
                is_asking_help = True
            elif is_asking_help and nav.nav_code and nav.nav_code < 6:
                '''recovered from stuck'''
                logging.info('Recovered from stuck: ', nav.nav_code)
                call.recovered_message(nav.nav_code)
                is_asking_help = False
        else:
            pass

        time.sleep(60/STATUS_CHECK_FREQ)


@app.route('/goto', methods=['POST'])
def travel_to():
    '''
    Travel to target station
    '''
    dest_station_id = request.get_json()['dest_station_id']
    logging.info(f'Start travel to dest_station_id : { dest_station_id} ')
    return ""
    


def bringup():
    '''
    Do all the bringup task here
    '''
    Thread(target=track_nav).run()
    




if __name__ == '__main__':
    logging.info('\n\n          -----BRAIN-----\n\n')
    bringup()
    app.run(host='0.0.0.0', port=8000, debug=True)


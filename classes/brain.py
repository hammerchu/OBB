#!/usr/bin/python
import os
import logging
from threading import Thread
import time
import asyncio
import json
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO

from bot.classes.navigate import Navigate
from bot.classes.plan import Plan
from bot.classes.call import Call
from bot.tools import zone_cmd
from bot.tools.monitor import Monitor
from bot.tools import profile

import coloredlogs, logging, verboselogs
logger = verboselogs.VerboseLogger(__name__)
# logger.basicConfig(level=logger.DEBUG)
coloredlogs.install(level='VERBOSE')


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


# from flask import Flask, request
# from flask_cors import CORS
# from threading import Thread
# import asyncio
# import logging
# import time

# from bot.classes.navigate import Navigate
# from bot.classes.plan import Plan
# from bot.classes.call import Call

# logging.basicConfig(level=logging.INFO)


class RobotControlCenter:
    def __init__(self):
        self.app = Flask(__name__, static_url_path="", static_folder="static")
        self.app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
        CORS(self.app)

        self.STATUS_CHECK_FREQ = 20
        self.nav = None
        self.plan = None
        self.call = None
        self.call_framerate = 60
        self.call_save_to_disk = False

        self.zone_cmd_in_run = []

        self.take_over_mode = False # eval first
        self.supervise_mode = False

        
        

    def start_call(self):
        self.call = Call('M', self.call_framerate, self.call_save_to_disk)  # Call and Streaming instance
        self.call.run('https://onbotbot.daily.co/_test')

    def quit_call(self):
        if self.call:
            self.call.leave()

    def action_thread(self):
        '''
        Running in a separate thread based on STATUS_CHECK_FREQ
        
        - Check if bot stuck
        - Communicate with HUBS if needed
        - Check control map color and run zone cmd
        '''
        is_asking_help = False
        
        while True:

            # if self.nav and self.call and self.plan and self.nav.is_navigating:
            if self.nav and self.plan and self.nav.is_on_nav:
                if not is_asking_help and self.nav.code and self.nav.code >= 6:
                    '''ask for help from HUBS'''
                    logger.critical('~~~~ Stuck: ', self.nav.code)
                    # self.call.stuck_message(self.nav.nav_code)
                    is_asking_help = True
                elif is_asking_help and self.nav.code and self.nav.code < 6:
                    '''recovered from stuck'''
                    logger.success('~~~~ Recovered from stuck: ', self.nav.code)
                    # self.call.recovered_message(self.nav.nav_code)
                    is_asking_help = False
            else:
                pass
            
            self.run_location_based_cmd() 

            time.sleep(60 / self.STATUS_CHECK_FREQ)

    
    def run_location_based_cmd(self):
        '''
        check if the current control map color is matching a zone
        If yes, run the preset zone cmd
        '''
        map_zone_cmd = json.load(open(profile.MAP_DATA_JSON, 'r'))['map_zone_cmd']
        color_list = list(map(lambda x: x['color'], map_zone_cmd))
        cmd_list = list(map(lambda x: x['cmd'], map_zone_cmd))

        for index, color in enumerate(color_list):
            if self.nav:
                logger.info(f'~~~~~~~~ control map color: {self.nav.control_map_color} ')

                # if BOT step on control color and the action is not currently running
                if self.nav.control_map_color == color and cmd_list[index] not in self.zone_cmd_in_run:

                    # Add the action to an active cmd list to avoid repetitive runs
                    self.zone_cmd_in_run.append(cmd_list[index])
                    r = eval(f"zone_cmd.{cmd_list[index]}(self, self.nav)")
                    if r:
                        # if the cmd is done, remove the action from the active cmd list
                        self.zone_cmd_in_run.remove(cmd_list[index])



    def index(self):
        return 'Hello OBB'
    

    def travel_to(self):
        '''
        Travel to target station
        '''
        dest_station_id = request.get_json()['dest_station_id']
        logger.info(f'~~~~~~~~ Start travel to dest_station_id : {dest_station_id} ')
        return ""


    def bringup(self):
        '''
        Do all the bringup task here
        '''
        self.nav = asyncio.run(Navigate._init_())  # Nav instance
        self.plan = Plan()  # Plan instance
        self.start_call()
        
        Thread(target=self.action_thread).start()


    def start(self, ui=False):
        logger.info('\n\n ~~~~~~ BRAIN ~~~~~~\n\n')
        self.bringup()

        self.app.add_url_rule('/', 'index', self.index, methods=['GET'])
        self.app.add_url_rule('/goto', 'travel_to', self.travel_to, methods=['POST'])
        self.app.run(host='0.0.0.0', port=8000, debug=True)

        if ui:
            self.ui = Monitor(self.nav, load_connection=False, load_controller=False)
        else:
            self.ui = None


if __name__ == '__main__':
    robot_control_center = RobotControlCenter()
    robot_control_center.start(ui=True)


# app = Flask(__name__, static_url_path="", static_folder="static")
# app.config.from_object('config')
# app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
# CORS(app)

# STATUS_CHECK_FREQ = 20 

# nav = asyncio.run(Navigate._init_()) # Nav instance
# plan = Plan() # Plan instance
# call = Call('M', 60, 0) # Call and Streaming instance
# call.run('https://onbotbot.daily.co/_test')

# def track_nav():
#     '''
#     Running in a separate thread to check if bbot stuck
#     '''
#     is_asking_help = False
#     while True:
#         call.heart_beat() # Send heart beat

#         if nav.is_navigating:
#             logging.debug('Nav code: ', nav.nav_code)
#             if not is_asking_help and nav.nav_code and nav.nav_code >= 6:
#                 '''ask for help from HUBS'''
#                 logging.info('Stuck: ', nav.nav_code)
#                 call.stuck_message(nav.nav_code)
#                 is_asking_help = True
#             elif is_asking_help and nav.nav_code and nav.nav_code < 6:
#                 '''recovered from stuck'''
#                 logging.info('Recovered from stuck: ', nav.nav_code)
#                 call.recovered_message(nav.nav_code)
#                 is_asking_help = False
#         else:
#             pass

#         time.sleep(60/STATUS_CHECK_FREQ)


# @app.route('/goto', methods=['POST'])
# def travel_to():
#     '''
#     Travel to target station
#     '''
#     dest_station_id = request.get_json()['dest_station_id']
#     logging.info(f'Start travel to dest_station_id : { dest_station_id} ')
#     return ""
    


# def bringup():
#     '''
#     Do all the bringup task here
#     '''
#     Thread(target=track_nav).run()
    




# if __name__ == '__main__':
#     logging.info('\n\n          -----BRAIN-----\n\n')
#     bringup()
#     app.run(host='0.0.0.0', port=8000, debug=True)




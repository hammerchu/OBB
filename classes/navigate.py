#-*-coding:utf-8-*-
from typing import Tuple, List, Dict # for python 3.8
from threading import Thread
import logging
import asyncio
import time
from datetime import datetime

from bot.classes.connection import Connect
from bot.classes.plan import Plan
from bot.tools.utilities import get_scaled_control_map_color
from bot.tools import profile, utilities

logging.basicConfig(level=logging.INFO)


class Navigate():
    '''
    This class represent the nagivation functionalities of a bot

    Running on the PI  
    '''

    def __init__(self):
        self.id = profile.id
        self.model = profile.model

        try:
            self.connection = Connect('192.168.1.102') # connect to Navis
            self.plan = Plan() # Goal list planner
        except Exception as e:
            logging.error("Unable to connect", e)


        self.map_station_steps = []
        self.current_map = None
        self.current_task = None
        self.current_task_index = 0
        
        self.code = None # status code report from BOT
        self.is_on_nav = False # True if NAV is running
        self.is_on_task = False # True if NAV is travelling to a task/goal
        self.progress = 0
        self.is_arrived_dest = False # True if NAV has arrived at its dest
        self.TRACK_FREQ = 30 
        self.UPDATE_FREQ = 60 

        self.px = None
        self.py = None
        self.pz = None
        self.ox = None
        self.oy = None
        self.oz = None
        self.oz = None

        self.control_map_color = (-1, -1, -1, -1)

        self.gps_status = None
        self.gps_lat = -1
        self.gps_lng = -1

    
    async def nav_bringup(self):
        '''
        Check and update nav info, run at startup
        '''
        r = await self.connection.get_nav_status()
        if r and r[0]: # r[0] -> nav_status  
            self.nav_mode = True # bot nav mode is ON
        else:
            # start nav mode....
            
            # re-check if nav is on
            pass

        time.sleep(2)

        # Run the nav tracking thread
        self.update_nav_thread = Thread(target = self.update_nav)
        self.update_nav_thread.run()
        logging.info('===== Run Nav bringup =====')
    
    @classmethod
    async def _init_(cls):
        self = cls()
        await self.nav_bringup()
        return self

    
    def travel_to_station(self, dest_map, dest_station):
        '''
        Travel to dest station from the BOT's current position based on the shortest map-steps

        0 - Cancel any active dest
        1 - Get a list of map-step from current map e.g. [{'goal_map_name': 'T001', 'goal_station': 'T003'}, {'goal_map_name': 'T003', 'goal_station': 'T005'}, {'goal_map_name': 'T005', 'goal_station': 'S503'}] 
        2 - Finding the next mini-goal station for getting to the next map-step
        '''
        # Preparation
        self.is_arrived_dest = False
        self.is_on_task = True

        # Get the steps for the new task
        self.map_station_steps = self.plan.get_map_station_steps(self.current_map, dest_map, dest_station)
        
        # Launch the NAV on the steps above
        if self.map_station_steps:
            self.travel_to(self.map_station_steps[self.current_task_index]['goal_station'])



    '''
    Track NAV
    '''
    def track_nav(self):
        '''
        Running in a separate Thread to track the progress of NAV:\n

        - If BOT is arriving at goal, and launch them onto the next goal if they did
        - If BOT has arrived dest, launch dest_process
        '''
        index = 0
        while True:
            if self.is_on_task and self.map_station_steps and self.current_task_index >= len(self.map_station_steps) : # if BOT is on a task
                
                if self.code == 3 and self.is_arrived_dest: # if BOT arrived at dest # 3:任务完成
                    '''
                    Arriving at dest station  # 3:任务完成
                    '''
                    logging.info(f'NAV: Task Completed')
                    self.current_task_index = 0 # reset key variable
                    # Ask HUBS for the next task

                elif self.code == 3 and self.map_station_steps and self.current_task_index < len(self.map_station_steps) : 
                    '''
                    Arriving goal of each step  # 3:任务完成
                    '''
                    # update the task index
                    logging.info(f'NAV: arrived at goal {self.current_task_index} - {self.map_station_steps[self.current_task_index]} on {self.current_map}')
                    self.current_task_index += 1
                    # set the current_map to the next map
                    self.current_map = self.map_station_steps[self.current_task_index]['goal_map_name']
                    # launch travel to the next step-goal
                    logging.info(f'NAV: launching at goal {self.current_task_index} - {self.map_station_steps[self.current_task_index]} on {self.current_map}')
                    self.travel_to(self.map_station_steps[self.current_task_index]['goal_station'])
                
                elif self.code == 1: # 1:正在执行任务
                    if index % 3 == 0:
                        logging.info(f'NAV {self.nav_code2msg(self.code)} - progress: { str(self.progress).zfill(2)} of task{self.current_task_index}/{len(self.map_station_steps)}' )
                    else:
                        pass

                elif self.code == 7 or self.code == 8: # 7:异常状态 or 8:任务异常暂停
                    logging.info(f'NAV: {self.nav_code2msg(self.code)}  task{self.current_task_index}/{len(self.map_station_steps)}' )
                    # Ask for instruction from HUBS


                elif self.code == 6: # 6:定位丢失
                    logging.info(f'NAV: {self.nav_code2msg(self.code)}  task{self.current_task_index}/{len(self.map_station_steps)}' )
                    # Ask for help from HUBS
            else:
                if index % 3 == 0:
                    logging.info(f'NAV: no task to track')

            time.sleep(60/self.TRACK_FREQ)
            index += 1


    
    def travel_to(self, dest_station):
        '''
        Launch NAV on the dest station (must be on the current_map)\n

        if success, updates is_on_task to True
        '''
        # make sure dest station is on the current_map
        if not self.plan.is_station_on_map(self.current_map, dest_station):
            logging.error('NAV: Destination not on the current_map')
        else:
            task_name = f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}-{self.current_map}-{dest_station}'
            dest_station_position = self.plan.get_station_position(self.current_map, dest_station)
            if self.current_map:
                # add a new task to the BOT
                r_task = self.connection.set_list_task(self.current_map, task_name, dest_station_position)
                if r_task:
                    # Run the new task
                    r_run = self.connection.run_list_task(self.current_map, task_name)
                    if r_run:
                        self.is_on_task = True
                    else:
                        logging.error('Failed to run_list_task')
                        self.is_on_task = False
                else:
                    logging.error('Failed to set_list_task')
                


    async def nav_action(self, task, action):
        '''
        Pause, resume or cancel an existing task from, usually because we need to launch a new one
        '''
        await self.connection.nav_action(self.current_map, action)
        if action == 'cancel':
            await self.connection.cmd_vel() # stop
    

    def dest_process(self):
        '''
        A sequence of action to do when BOT arrived at dest, including inform HUBS, \n
        prepare for unlock compartment, etc
        '''
        pass


    '''
    Update NAV
    '''
    async def update_nav(self):
        '''
        Running in a separate Thread to update:\n
         - current map\n
         - current task\n
         - current position on map\n
         - Nav status code\n
         - Nav progress\n
         - color code from control map
        '''
        index = 0
        while True:
            if self.is_on_nav:
                if index % 5 == 0:
                    logging.info('NAV: updates')
                await self.update_nav_code_and_current_map()
                await self.update_position_in_current_map()
                await self.update_progress()
                self.update_control_map_color()
            else:
                pass
               
            time.sleep(60/self.UPDATE_FREQ)
    
    async def update_nav_status(self):
        '''
        Get the bot's current position in the current map
        '''
        if self.current_map and await self.connection.get_nav_localization():
            resp = await self.connection.get_nav_status()
            if resp:
                self.nav_status, _, self.current_task = resp
            else:
                logging.info('WARNING - unable to update current BOT status, map and task')
        else:
            logging.info(f'{self.id} is not in navigation mode')
    
    async def update_progress(self):
        '''
        Get the bot's current position in the current map
        '''
        if self.current_map and await self.connection.get_nav_localization():
            resp = await self.connection.get_nav_progress()
            if resp:
                self.progress = resp
            else:
                logging.info('WARNING - unable to update current BOT position on map')
        else:
            logging.info(f'{self.id} is not in navigation mode')

    async def update_position_in_current_map(self):
        '''
        Get the bot's current position in the current map
        '''
        if self.current_map and await self.connection.get_nav_localization():
            resp = await self.connection.get_bot_position()
            if resp:
                self.px, self.py, self.pz, self.ox, self.oy, self.oz, self.oz = resp
            else:
                logging.info('WARNING - unable to update current BOT position on map')
        else:
            logging.info(f'{self.id} is not in navigation mode')


    def update_control_map_color(self):
        '''
        Takes an image_position and a map_name and return a rgb color for that image_position
        '''
        if self.current_map:
            resp = get_scaled_control_map_color(self.current_map, (self.px, self.py))
            if resp:
                self.control_map_color = resp
                
            else:
                logging.info('WARNING - map_color not updated')
        else:
            logging.info('WARNING - current_map unavailable')

    
    async def update_nav_code_and_current_map(self):
        '''
        Check and update nav status code - valid when nav mode is ON
        '''
        resp = await self.connection.get_navi_code()
        if resp:
            status_code, map_name, text = resp # type: ignore
            try:
                self.code = int(status_code)
                self.current_map = map_name
                logging.debug(f' self.nav_code : { self.code} ')
            except Exception as e:
                logging.error(e)

        else:
            logging.error('NAV: Unable to obtain nav code')

    '''
    Utilities
    '''
    def nav_code2msg(self, code) -> str:
        nav_code_label = {
            '0' : '等待新任务',
            '1' : '正在执行任务',
            '2' : '取消任务',
            '3' : '任务完成',
            '4' : '任务中断',
            '5' : '任务暂停',
            '6' : '定位丢失',
            '7' : '异常状态',
            '8' : '任务异常暂停',
            '9' : '机器人充电',
        }
        return nav_code_label[str(code)]



async def main():
     nav = await Navigate._init_()
     return 




if __name__ == '__main__':
    asyncio.run(main())
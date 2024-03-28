#-*-coding:utf-8-*-
from typing import Tuple, List, Dict # for python 3.8
import math
from threading import Thread
import time
from datetime import datetime

import asyncio
import nest_asyncio

from bot.classes.connection import Connect
from bot.classes.plan import Plan
from bot.tools.utilities import get_scaled_control_map_color
from bot.tools import profile, utilities

nest_asyncio.apply()

import coloredlogs, logging, verboselogs
logger = verboselogs.VerboseLogger(__name__)
# logger.basicConfig(level=logger.DEBUG)
coloredlogs.install(level='VERBOSE')



class Navigate():
    '''
    This class represent the nagivation functionalities of a bot

    Running on the PI  
    '''

    def __init__(self):
        logger.notice('Running __init__')
        self.id = profile.id
        self.model = profile.model

        try:
            self.connection = Connect('192.168.1.102') # connect to Navis
            self.plan = Plan() # Goal list planner
        except Exception as e:
            logger.error("Unable to connect", e)


        self.map_station_steps = []
        self.current_map = None
        self.current_task = None
        self.current_task_index = 0
        self.current_goal_position = None
        
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
        self.ow = None

        self.control_map_color = (-1, -1, -1, -1)


        self.dist_from_goal = None

        self.gps_status = None
        self.gps_lat = -1
        self.gps_lng = -1

    
    async def nav_bringup(self):
        '''
        Check and update nav info, run at startup
        '''
        logger.notice('----- Running bring up -----')

        r = await self.connection.get_nav_status()
        if r: # r[0] -> nav_status  
            self.nav_mode = True # bot nav mode is ON
            self.nav_status = r[0]
            self.current_map = r[1]
            self.current_task = r[2]
            self.is_on_nav = True
            print(f' NAV: is_on_nav : { self.is_on_nav} ')
            print(f' NAV: current_map : { self.current_map} ')
            print(f' NAV: current_task : { self.current_task} ')
        else:
            # start nav mode....
            
            # re-check if nav is on
            pass

        time.sleep(2)

        # Run the nav tracking thread
        # self.update_nav_thread = Thread(target = self.update_nav)
        self.update_nav_thread = Thread(target = self.update_nav_wraper)
        self.track_nav_thread = Thread(target = self.track_nav)
        self.track_nav_thread.start()
        self.update_nav_thread.start()
    
    @classmethod
    async def _init_(cls):
        logger.notice('Running _init_')
        self = cls()
        await self.nav_bringup()
        return self

    
    def travel_to_station(self, dest_map, dest_station, start=None):
        '''
        Travel to dest station from the BOT's current position based on the shortest map-steps

        0 - Cancel any active dest
        1 - Get a list of map-step from current map e.g. [{'goal_map_name': 'T001', 'goal_station': 'T003'}, {'goal_map_name': 'T003', 'goal_station': 'T005'}, {'goal_map_name': 'T005', 'goal_station': 'S503'}] 
        2 - Finding the next mini-goal station for getting to the next map-step
        '''
        # Preparation
        self.is_arrived_dest = False
        self.is_on_task = True
        
        if not start:
            current_map = self.current_map

        # Get the steps for the new task
        self.map_station_steps = self.plan.get_map_station_steps(current_map, dest_map, dest_station)

        print(f'\n ----- map_station_steps {self.map_station_steps} -----\n' )
        
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
            print(f'\n ****** TRACK NAV ****** ') 
            print('is_on_nav', self.is_on_nav)
            print('map_station_steps', self.map_station_steps )
            print('current_task_index', self.current_task_index)

            print(f'\n') 
            # logger.info(f'\n ****** TRACK NAV ****** ') 
            # logger.info(self.is_on_nav)
            # logger.info(self.map_station_steps )
            # logger.info(self.current_task_index)
            # logger.info(self.map_station_steps)
            # logger.info(f'\n') 
            if self.is_on_nav:

                # elif self.dist_from_goal and self.dist_from_goal < 0.3  and self.map_station_steps and self.current_task_index < len(self.map_station_steps) : 
                if self.dist_from_goal and self.dist_from_goal < 0.3 and self.map_station_steps: 
                    if self.current_task_index + 1 < len(self.map_station_steps):
                        '''
                        Arriving goal of each step  # 3:任务完成
                        '''
                        print(f'****** Arrived at step goal {self.current_task_index} - {self.map_station_steps[self.current_task_index]} on {self.current_map}')
                        logger.success(f'****** Arrived at step goal {self.current_task_index} - {self.map_station_steps[self.current_task_index]} on {self.current_map}')
                        
                        # update the task index 
                        self.current_task_index += 1

                        # set the current_map to the next map
                        self.current_map = self.map_station_steps[self.current_task_index]['goal_map_name']
                        
                        # launch travel to the next step-goal
                        print(f'****** launching at goal {self.current_task_index} - {self.map_station_steps[self.current_task_index]} on {self.current_map}')
                        logger.success(f'****** launching at goal {self.current_task_index} - {self.map_station_steps[self.current_task_index]} on {self.current_map}')
                        self.travel_to(self.map_station_steps[self.current_task_index]['goal_station'])
                    else:
                        '''
                        Arriving at the last station  # 3:任务完成
                        '''
                        print('****** Station arrived ******\n')
                        logger.success('****** Station arrived ******\n')
                        self.is_arrived_dest = True
                        self.current_task_index = 0 # reset key variable
                        # Ask HUBS for the next task

                
                elif self.code == 1: # 1:正在执行任务
                    if index % 3 == 0:
                        print(f'****** {self.nav_code2msg(self.code)} - progress: { str(self.progress).zfill(2)} of task{self.current_task_index}/{len(self.map_station_steps)} ' )
                        logger.success(f'****** {self.nav_code2msg(self.code)} - progress: { str(self.progress).zfill(2)} of task{self.current_task_index}/{len(self.map_station_steps)} ' )
                    else:
                        pass

                elif self.code == 7 or self.code == 8: # 7:异常状态 or 8:任务异常暂停
                    print(f'****** WARNING - Error - {self.nav_code2msg(self.code)}  task{self.current_task_index}/{len(self.map_station_steps)}' )
                    logger.success(f'****** WARNING - Error - {self.nav_code2msg(self.code)}  task{self.current_task_index}/{len(self.map_station_steps)}' )
                    # Ask for instruction from HUBS


                elif self.code == 6: # 6:定位丢失
                    logger.success(f'****** WARNING - Localization failed - {self.nav_code2msg(self.code)}  task{self.current_task_index}/{len(self.map_station_steps)}' )
                    # Ask for help from HUBS
            else:
                if index % 3 == 0:
                    logger.success(f'****** No task to track')

            time.sleep(60/self.TRACK_FREQ)
            index += 1


    
    def travel_to(self, dest_station):
        '''
        Launch NAV on the dest station (must be on the current_map)\n

        if success, updates is_on_task to True
        '''
        print(f' >>>>> TRAVEL TO >>>>>') 
        # make sure dest station is on the current_map
        if not self.plan.is_station_on_map(self.current_map, dest_station):
            logger.verbose('>>>>>  Destination not on the current_map')
            return None
        else:
            task_name = f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}-{self.current_map}-{dest_station}'
            dest_station_position = self.plan.get_station_position(self.current_map, dest_station)
            self.current_goal_position = dest_station_position
            print(f'>>>>> dest_station_position : { self.current_goal_position} ')
            logger.verbose(f'>>>>> dest_station_position : { self.current_goal_position} ')
            if self.current_map:
                # add a new task to the BOT
                r_task = self.connection.set_list_task(self.current_map, task_name, [dest_station_position])
                if r_task:
                    # Run the new task
                    r_run = self.connection.run_list_task(self.current_map, task_name)
                    if r_run:
                        self.is_on_task = True
                        return True
                    else:
                        logger.error('Failed to run_list_task')
                        self.is_on_task = False
                        return None
                else:
                    logger.error('Failed to set_list_task')
                    return None
                


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

    def update_nav_wraper(self):
        asyncio.run(self.update_nav())
       

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
                if index % 1 == 0:
                    print(f'\n===== NAV =====')
                    print(f'=== nav_code: {self.code}')
                    print(f'=== current_map: {self.current_map}')
                    print(f'=== current_task: {self.current_task}')
                    print(f'=== current_goal: {self.current_goal_position}')
                    print(f'=== position: {self.px}, {self.py}')
                    print(f'=== progress: {self.progress}')
                    print(f'=== dist from goal: {self.dist_from_goal}')

                    # logger.info('NAV: updates')
                await self.update_nav_code_and_current_map()
                await self.update_progress()
                await self.update_position_in_current_map()
                self.update_control_map_color()

                self.dist_from_goal = self.dist_btw_positions((self.px, self.py), self.current_goal_position)

            else:
                pass
               
            time.sleep(60/self.UPDATE_FREQ)
            index += 1
    
    async def update_nav_status(self):
        '''
        Get the bot's current position in the current map
        '''
        if self.current_map and await self.connection.get_nav_localization():
            resp = await self.connection.get_nav_status()
            if resp:
                self.nav_status, _, self.current_task = resp
            else:
                logger.info('WARNING - unable to update current BOT status, map and task')
        else:
            logger.info(f'{self.id} is not in navigation mode')
    

    async def update_progress(self):
        '''
        Get the bot's current position in the current map
        '''
        if self.is_on_nav:
            resp = await self.connection.get_nav_progress()
            print(f'=== update_progress : { resp} ')
            if resp:
                self.progress = resp
            else:
                logger.info('WARNING - unable to update current BOT position on map')
        else:
            logger.info(f'{self.id} is not in navigation mode')


    async def update_position_in_current_map(self):
        '''
        Get the bot's current position in the current map
        '''
        if self.is_on_nav:
            resp = await self.connection.get_bot_position()
            print(f'=== update_position_in_current_map : { resp} ')
            if resp:
                self.px, self.py, self.pz, self.ox, self.oy, self.oz, self.oz = resp
            else:
                logger.info('WARNING - unable to update current BOT position on map')
        else:
            logger.info(f'{self.id} is not in navigation mode')


    def update_control_map_color(self):
        '''
        Takes an image_position and a map_name and return a rgb color for that image_position
        '''
        if self.current_map and self.px != None  and self.py != None:
            resp = get_scaled_control_map_color(self.current_map, (self.px, self.py))
            if resp:
                print(f'=== update_control_map_color : { resp} ')
                self.control_map_color = resp
                
            else:
                logger.info('WARNING - map_color not updated')
        else:
            logger.info('WARNING - current_map unavailable')

    
    async def update_nav_code_and_current_map(self):
        '''
        Check and update nav status code - valid when nav mode is ON
        '''
        resp = await self.connection.get_navi_code()
        print(f'=== update_nav_code_and_current_map : { resp} ')
        if resp!= None:
            status_code = resp # type: ignore
            try:
                self.code = int(status_code)
                # self.current_map = map_name
                logger.debug(f' self.nav_code : { self.code} ')
            except Exception as e:
                logger.error(e)

        else:
            logger.error('NAV: Unable to obtain nav code')

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

    def dist_btw_positions(self, position1, position2):
        '''
        '''
        x_sq = (position1[0] - position2[0])**2 
        y_sq = (position1[1] - position2[1])**2
        distance = math.sqrt(x_sq + y_sq)
        return distance

async def main():
     nav = await Navigate._init_()

     nav.travel_to_station('T005', 'S503', 'T001' )
     return 




if __name__ == '__main__':
    asyncio.run(main())
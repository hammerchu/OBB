#-*-coding:utf-8-*-
from threading import Thread
from connection import Connect
from plan import Plan
from typing import Tuple, List, Dict # for python 3.8
from tools import profile, utilities
import logging
import asyncio
import time

logging.basicConfig(level=logging.INFO)


class Navigate():
    '''
    This class represent the nagivation functionalities of a bot

    Running on the PI  
    '''

    def __init__(self):
        self.id = profile.id
        self.model = profile.model

        self.connection = Connect('192.168.1.102') # connect to Navis
        self.plan = Plan() # Goal list planner
        
        self.nav_mode = False
        self.nav_code = None
        self.is_navigating = False
        self.current_map = None
        self.mini_goal_index = 0
        self.POSITION_CHECK_FREQ = 60 # check status 10 times one min

        self.px = -1
        self.py = -1
        self.pz = -1
        self.ox = -1
        self.oy = -1
        self.oz = -1
        self.oz = -1

        self.control_map_color = (-1, -1, -1)

        self.gps_status = None
        self.gps_lat = -1
        self.gps_lng = -1

    
    async def nav_bringup(self):
        '''
        Check and update nav info, run at startup
        '''
        if self.connection.is_nav_on():
            self.nav_mode = True # bot nav mode is ON
        else:
            # start nav mode....
            
            # re-check if nav is on
            pass

        time.sleep(2)

        # Run the nav tracking thread
        self.track_nav_thread = Thread(target = self.track_nav)
        self.track_nav_thread.run()
        logging.info('Run Nav bringup')
    
    @classmethod
    async def _init_(cls):
        self = cls()
        await self.nav_bringup()
        return self

    async def update_nav_code_and_current_map(self):
        '''
        Check and update nav status code - valid when nav mode is ON
        '''
        resp = await self.connection.get_navi_code()
        if resp:
            status_code, map_name, text = resp # type: ignore
            try:
                self.nav_code = int(status_code)
                self.current_map = map_name
                logging.debug(f' self.nav_code : { self.nav_code} ')
            except Exception as e:
                logging.error(e)

        else:
            logging.error('Unable to obtain nav code')

    
    def goto_next_mini_goal(self) -> Tuple[float, float] :
        '''
        Tell the bot to travel to the next mini goal
        '''
        lat = 23.2345566
        lng = 248.234566
        dest = (lat, lng)
        return dest
    

    def update_gps_position(self):
        '''
        get gps position from bot
        '''
        self.gps_lat = -1
        self.gps_lng = -1
    

    async def update_position_in_current_map(self):
        '''
        Get the bot's current position in the current map
        '''
        if self.current_map and await self.connection.get_nav_localization():
            resp = await self.connection.get_bot_position()
            if resp:
                self.px, self.py, self.pz, self.ox, self.oy, self.oz, self.oz = resp
        else:
            logging.info(f'{self.id} is not in navigation mode')

    def update_control_map_color(self, map_name:str, map_position: Tuple[int, int]):
        '''
        Takes an image_position and a map_name and return a rgb color for that image_position
        '''
        self.control_map_color = (-1, -1, -1)
    


    '''
    Threads
    '''

    async def track_nav(self):
        '''
        Running in a separate Thread to update:\n
         - current map\n
         - current position on map\n
         - Nav status code
        '''
        while True:
            if self.is_navigating:
                await self.update_position_in_current_map()
                await self.update_nav_code_and_current_map()
               
            time.sleep(60/self.POSITION_CHECK_FREQ)


async def main():
     nav = await Navigate._init_()
     return 




if __name__ == '__main__':
    asyncio.run(main())
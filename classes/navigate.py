#-*-coding:utf-8-*-
from typing import Tuple, List, Dict # for python 3.8
from tools import profile, utilities
import logging

logging.basicConfig(level=logging.INFO)

class Navigate():
    '''
    This class represent the nagivation functionalities of a bot

    Running by the PI  
    '''

    def __init__(self):
        self.id = profile.id
        self.model = profile.model
        self.is_navigating = False
        self.current_map = None


    def check_navigation_status(self) -> bool:
        status = False
        return False
    
    def get_next_dest(self) -> Tuple[float, float] :
        '''
        Obtain the next navigation goal regardless finishing the current goal or not
        '''
        lat = 23.2345566
        lng = 248.234566
        dest = (lat, lng)
        return dest

    def start_navigate(self):
        '''
        Initalize navigation to ward the next goal
        '''
        pass

    def get_gps_position(self):
        '''
        get gps position from bot
        '''
        lat = -1
        lng = -1

        return lat, lng
    

    def gps_to_map_position(self, gps_position: Tuple[float, float]) -> Dict[str, Tuple[int, int]]:
        '''
        Takes a gps data and turn that into ROS map_name and image_position pairs
        '''

        result = {'map_name': 'T001', 'map_position': (255, 33)} # example
        return result

    def get_map_color(self, map_name:str, map_position: Tuple[int, int]) -> Tuple[int, int, int]:
        '''
        Takes an image_position and a map_name and return a rgb color for that image_position
        
        '''
        result = (0, 0, 0)
        return result

    # def get_health(self):
    #     '''
    #     check the health of the bot and the connectivity
    #     '''
    #     pass


def main():
    pass



if __name__ == '__main__':
    
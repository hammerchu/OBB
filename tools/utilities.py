from typing import Tuple, List, Dict, Union # for python 3.8
from PIL import Image
import os
import yaml
from bot.tools import profile
import logging

'''
Utilities functions
'''
def timer(some_function):
    from time import time

    def wrapper(*args, **kwargs):
        t1 = time()
        result = some_function(*args, **kwargs)
        end = time()-t1
        return result, end
    return wrapper

def convert_map_to_png_pos(map_name:str, position:Tuple[int, int], gridWidth:int=0, gridHeight:int=0):
    '''
    convert map coord to map image position
    '''
    # read data from map yaml
    try:
        yaml_path = os.path.join(profile.ROOT_PATH, f'data/maps/{map_name}/{map_name}.yaml')
        with open(yaml_path, 'r') as file :
            map_yaml = yaml.safe_load(file)
        print(f' map_yaml : { map_yaml} ')

        # If map image size is not provided, found it out
        if gridWidth == 0 or gridHeight == 0:
            map_img_path = os.path.join(profile.ROOT_PATH, f'data/maps/{map_name}/{map_name}.png')
            gridWidth, gridHeight = Image.open(map_img_path).size
    
        pose_x = position[0]
        pose_y = position[1]
        originX = map_yaml['origin'][0]
        originY = map_yaml['origin'][1]
        resolution = map_yaml['resolution']
        
        png_x = (pose_x - originX) / resolution
        png_y = gridHeight - (pose_y - originY) / resolution

        return png_x, png_y

    except Exception as e:
        logging.error(e)

@timer
def get_control_map_color(map_name:str, position:Tuple[int, int]) -> Union[Tuple[int, int, int, int], None]:
    '''
    return pixel color of a control map of a map
    '''
    result = None
    control_map_img_path = os.path.join(profile.ROOT_PATH, f'data/maps/{map_name}/{map_name}_control.png')
    map_image = Image.open(control_map_img_path)
    gridWidth, gridHeight = map_image.size
    resp = convert_map_to_png_pos(map_name, position, gridWidth, gridHeight)
    if resp:
        png_x, png_y = resp
        print(f' x, y : { resp} ')
        result = map_image.getpixel((int(png_x), int(png_y)))
    return result


def get_scaled_control_map_color(map_name:str, position:Tuple[int, int]) -> Union[Tuple[int, int, int, int], None]:
    '''
    return pixel color of a control map of a map
    '''
    scale_factor = 5
    result = None
    control_map_img_path = os.path.join(profile.ROOT_PATH, f'data/maps/{map_name}/{map_name}_control_scaled.png')
    map_image = Image.open(control_map_img_path)
    gridWidth, gridHeight = map_image.size
    resp = convert_map_to_png_pos(map_name, position, gridWidth*scale_factor, gridHeight*scale_factor)
    if resp:
        png_x, png_y = resp
        print(f' x, y : { resp} ')
        result = map_image.getpixel((int(png_x/scale_factor), int(png_y/scale_factor)))
    return result




    
if __name__ == '__main__':
    # resp = convert_map_to_png_pos('T001-02', (0,0))
    # if resp:
    #     png_x, png_y = resp
    #     print(png_x, png_y)
    resp = get_control_map_color('T001-02', (0,0))
    if resp:
        print(resp)
    
    resp = get_scaled_control_map_color('T001-02', (0,0))
    if resp:
        print(resp)
    
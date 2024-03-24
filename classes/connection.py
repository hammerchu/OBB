#-*-coding:utf-8-*-
from typing import Tuple, List, Dict, Union
from urllib import response
import sys
import time
from datetime import datetime
import logging
import json
import random
import requests
import asyncio
import websockets
from asyncio import create_task, gather, sleep, run


logging.basicConfig(level=logging.ERROR)
# logging.getLogger("asyncio").setLevel(logging.WARNING)
# logging.getLogger('asyncio').setLevel(logging.ERROR)
# logging.getLogger('asyncio.coroutines').setLevel(logging.ERROR)
logging.getLogger('websockets.server').setLevel(logging.ERROR)
logging.getLogger('websockets.protocol').setLevel(logging.ERROR)

class Connect():
    '''
    Functionalities for all the key websocket connection requests with the agileX bots
    Manged by async send and feedback queues
    '''


    def __init__(self, bot_ip):
        self.bot_ip = bot_ip
        http_port = "8880"
        ws_port = "9090"
        self.http_url = f"http://{self.bot_ip}:{http_port}"
        self.ws_url = f"ws://{self.bot_ip}:{ws_port}"
        self.queue = asyncio.Queue()

        self.finish = False

        self.auth_token = ''

        self.timeout_limit = 3

        self.token = self.login()
        logging.debug(f' Token : { self.token} ')
        logging.info(f' Dev ver: {self.get_dev_ver()}\n\n')

        
        '''Test'''
        # task_points = [(0,0,0), (3, 0, 180) , (10, 0, 0)]
        # map_name='Elements04'
        # task_name='Element04_test_03'
        # print('\n')
        # self.set_list_task(map_name, task_name, task_points)
        # print('\n')
        # logging.info(f' Map list: {self.get_maps_list()}')
        


        # asyncio.run(self.run()) // error -> got Future <Future pending> attached to a different loop
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.run())


    def send_data_http(self, url, action, header, data) -> Union[Dict, None]:
        if action == 'get':
            resp = requests.get(url, headers=header, data=data, timeout=3)
            logging.debug(f'HTTP GET RETURN MSG: {resp.text}\n')
            if resp:
                return resp.json()
            else:
                logging.error(f'Failed to GET from {url}')
                return None
            
        elif action == 'post':
            # headers = {"Content-type": "application/json"}
            resp = requests.post(url, headers=header, data=json.dumps(data), timeout=3)
            resp.encoding = 'UTF-8' # or resp.apparent_encoding
            logging.debug(f'\nHTTP POST RETURN MSG v1.1: {resp.content}\n')
            if resp:
                return resp.json()
            else:
                logging.error(f'Failed to POST to {url}')
                return None
        else:
            logging.error(f'Error - unknown action {action}')
            return None
          

    async def send_data_ws(self, message):
        # uri = f"ws://{self.bot_ip}:9090" #填写实际的机器人IP地址:9090
        # uri = f"ws://192.168.1.102:9090" #填写实际的机器人IP地址:9090
        async with websockets.connect(self.ws_url) as websocket:
            try:
                await websocket.send(bytes(json.dumps(message, ensure_ascii=False).encode("utf-8")))
                # resp = asyncio.wait_for(websocket.recv(), timeout=self.timeout_limit)
                resp = await websocket.recv()
                # print(f' WS resp : { resp} \n')
                if resp:
                    return json.loads(str(resp))
                else:
                    return None
            except:
                return None
    

    async def send_data_ws_no_resp(self, message) -> Union[bool, None]:
        # uri = f"ws://{self.bot_ip}:9090" #填写实际的机器人IP地址:9090
        # uri = f"ws://192.168.1.102:9090" #填写实际的机器人IP地址:9090
        async with websockets.connect(self.ws_url) as websocket:
            try:
                await websocket.send(bytes(json.dumps(message, ensure_ascii=False).encode("utf-8")))
                return True
            except:
                return None
        
    async def mock_send_data(self, topic):
        logging.debug(f'{topic} sent')
        sleep_time = random.random()*5
        await sleep(sleep_time)
        logging.debug(f'{topic} done after {sleep_time}s')
        return f'{topic}_{sleep_time}'
    
    async def rnd_sleep(self, t):
        # sleep for T seconds on average
        # await asyncio.sleep(t * random.random() * 2)
        await asyncio.sleep(t)
    
    async def producer_original(self, label=1):
        logging.debug(f'------P{label}------')
        while True:
            # produce a token and send it to a consumer
            token = random.random()
            logging.debug(f'produced {token}    {time.time()}')
            if token < .05:
                break
            await self.queue.put(token)
            await self.rnd_sleep(token*3)

    async def producer(self, label=1):
        logging.debug(f'------P{label}------')
        while True:
            # produce a token and send it to a consumer
            token = random.random()
            logging.debug(f'produced {token}    {time.time()}')
            if token < .05:
                break
            await self.queue.put(token)
            await self.rnd_sleep(token*3)
            
    async def consumer_original(self, label=1):
        logging.debug(f'======C{label}======')
        while True:
            token = await self.queue.get()
            # process the token received from a producer
            await self.rnd_sleep(.3)
            self.queue.task_done()
            logging.debug(f'    consumed {token}    {time.time()}')

    async def consumer(self, label=1):
        logging.debug(f'======C{label}======')
        while True:
            token = await self.queue.get()
            # process the token received from a producer
            await self.rnd_sleep(.3)
            self.queue.task_done()
            # print(f'    consumed {token}    {time.time()}')

    async def run(self):
        # fire up the both producers and consumers
        producers = [asyncio.create_task(self.producer(_))
                    for _ in range(3)]
        consumers = [asyncio.create_task(self.consumer(_))
                    for _ in range(3)]
    
        # with both producers and consumers running, wait for
        # the producers to finish
        await asyncio.gather(*producers)
        logging.debug('---- done producing')

        # wait for the remaining tasks to be processed
        await self.queue.join()
    
        # cancel the consumers, which are now idle
        for c in consumers:
            c.cancel()

    '''
    API functions
    '''

    def login(self):
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#登录请求

        return -> login Token
        '''
        action = 'post'
        # http://192.168.1.102:8880/user/passport/login
        url = f"{self.http_url}/user/passport/login"
        headers = {'Content-type': 'application/json'}
        data = {
            "username": "agilex",
            "password": "NTdhMTE5NGNiMDczY2U4YjNiYjM2NWU0YjgwNWE5YWU="
        }
        try:
            resp = self.send_data_http(url, action, headers, data)
            # resp = self.send_data_http(url, action, headers, params)
            if resp and resp['code'] == 0:
                return resp['data']
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None
        except Exception as e:
            logging.error(e)
            return None
        
    def get_dev_ver(self):
        action = 'get'
        url = f"http://{self.bot_ip}:8880/dev_version"
        headers = { "Authorization" : self.token }
        params = ""
        try:
            resp = self.send_data_http(url, action, headers, params)
            if resp and resp['code'] == 0:
                return resp
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None
        except Exception as e:
            logging.error(e)
            return None
    
    def get_maps_list(self):
        action = 'get'
        sort_type = 'time'
        is_reverse = 'true'
        url = f"http://{self.bot_ip}:8880/map_list?page=1&limit=-1&sortType={sort_type}&reverse={is_reverse}"
        headers = { "Authorization" : self.token }
        params = ""
        try:
            resp = self.send_data_http(url, action, headers, params)
            if resp and resp['code'] == 0 and resp['data']['mapList']:
                return resp['data']['mapList']
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None
            
        except Exception as e:
            logging.error(e)
            return None


    def set_list_task(self, map_name:str, task_name:str, points:List[List[float]], speed:float=2):
        '''
        Create a task on a map

        file:///Users/hammerchu/Downloads/user_api(1).html#设置某个地图的某个任务信息

        points -> List of tuple(x, y, theta)
        speed -> max 1.5
        '''
        task_points = []
        for index, point in enumerate(points):
            task_points.append({
                "isNew": False,
                "index": f"point-{index+1}",
                "pointType": "navigation",
                "pointName": "",
                "actions": [],
                "position": {
                    "x": point[0],
                    "y": point[1],
                    # "theta": point[2]
                    "theta": 0
                },
                "cpx": 0,
                "cpy": 0
                })

        payload = {
            "mode": "point",
            "speed": speed,
            "evadible": 1, # 1：避障，2：停障
            "points": task_points,
            "mapName": map_name,
            "taskName": task_name,
            "editedName": task_name,
            "gridItemIdx": 0,
            "remark": "for testing",
            "personName": "OBB"
        }
        action = 'post'
        url = f"{self.http_url}/set_task"

        headers = { "Authorization" : self.token, 'Content-Type': 'application/json' }
        try:
            resp = self.send_data_http(url, action, headers, data=payload)
            if resp and resp['code'] == 0:
                return resp
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None
        except Exception as e:
            logging.error(e)
            return None

    def run_list_task(self, map_name, task_name):
        '''
        Run a preset task on a map

        '''

        payload = {
            "mapName": map_name, 
            "taskName": task_name,
            "loopTime": 1
        }

        action = 'post'
        url = f"{self.http_url}/run_list_task"

        headers = { "Authorization" : self.token, 'Content-Type': 'application/json' }
        try:
            resp = self.send_data_http(url, action, headers, data=payload)
            if resp and resp['code'] == 0:
                return resp
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None
        except Exception as e:
            logging.error(e)
            return None


    '''
    websocket functions
    '''
    
    async def get_sensor_status(self) -> Union[Tuple[str, str, str], None]:
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#设备传感器状态
        '''
        message = {
            "op":"subscribe",
            "topic": "/sensor_status",
            "type": "tools_msgs/SensorStatus"
        }
        try:
            resp = await self.send_data_ws(message)
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            
            if resp and resp['msg']:
                RTK_status = resp['msg']['RTK_status']
                lidar_status = resp['msg']['lidar_status']
                camera_status = resp['msg']['camera_status']

                return (RTK_status, lidar_status, camera_status)
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None
    

    async def get_rtk_data(self) -> Union[Tuple[str, str, str], None]:
        '''
        Getting GPS data from RTK device

        file:///Users/hammerchu/Downloads/user_api(1).html#rtk-gps传感器数据
        '''
        message = {
            "op":"subscribe",
            "topic": "/gnss_status",
            "type": "tools_msgs/GnssStatus"
        }
        try:
            # resp = await self.send_data_ws(message)
            loop = asyncio.get_event_loop()
            resp = loop.run_until_complete(self.send_data_ws(message))
            loop.close()
            if resp and resp['msg']:
                status = resp['msg']['nav']
                name = resp['msg']['name']
                task = resp['msg']['task']
                return (status, name, task)
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None
    

    async def get_nav_status(self) -> Union[Tuple[bool, str, str], None]:
        '''
        Return nav status, map and task info\n
        nav_status -> True if bot's nav mode is ON\n
        map_name -> current map, return '' if no active map\n
        task_name -> current task, return '' if no active task\n
        '''
        message = {
            "op":"subscribe",
            "topic": "/slam_status",
            "type": "tools_msgs/slamStatus"
        }
        try:
            # resp = await self.send_data_ws(message)
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            resp = await self.send_data_ws(message)
            if resp and resp['msg']['nav']:
                nav_status = resp['msg']['nav']['state']
                map_name = resp['msg']['nav']['name']
                task_name = resp['msg']['nav']['task']
                return nav_status, map_name, task_name
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None
            
        except Exception as e:
            logging.error(e)
            return None
        

    async def start_nav(self, map_name) -> Union[bool, None]: # type: ignore
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#启动关闭导航
        '''
        message = {
            "op": "call_service",
            "service": "/input/op",
            "type":"tools_msgs/input",
            "args": {
                "file_name": map_name,
                "op_type":"start",
                "id_type":"navigation"
            }
        }
        try:
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            resp = await self.send_data_ws(message)
            print(f' resp : { resp} ')
            if resp and resp['values']:
                is_success = resp['values']['success'] 
                return is_success
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None


    async def get_navi_code(self) -> Union[str, None]: # type: ignore
        '''
        Getting navigation status\n
        status -> 
        0 : 等待新任务
        1 : 正在执行任务
        2 : 取消任务
        3 : 任务完成
        4 : 任务中断
        5 : 任务暂停
        6 : 定位丢失
        7 : 异常状态,一般最后一个点无法到达会反馈此状态
        8 : 任务异常暂停，一般中间某个点无法到达会反馈此状态
        9 : 机器人充电会反馈此状态，此时任何对任务的操作都要失效\n 
        map_name -> 当前导航所用的地图名称\n 
        text -> 提示消息\n
        file:///Users/hammerchu/Downloads/user_api(1).html#导航系统状态
        '''
        message = {   
            "op": "subscribe",
            "topic": "/run_management/global_status",
            "type":"support_ros/GlobalStatus" 
        }
        try:
            resp = await self.send_data_ws(message)
            if resp and resp['msg']:
                status = resp['msg']['status'] # e.g. 1 : 正在执行任务
                return status
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None
    

    async def get_navi_path(self) -> Union[List[Dict], None]: # type: ignore
        '''
        Getting navigation path

        file:///Users/hammerchu/Downloads/user_api(1).html#获取导航规划路径
        '''
        message = {   
            "op": "subscribe",
            "topic": "/run_management/visual_path",
            "type":"nav_msgs/Path" 
        }
        try:
            resp = await self.send_data_ws(message)
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            if resp and resp['msg']['poses']:
                path = resp['msg']['poses']
                return path
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None


    async def get_nav_progress(self) -> Union[float, None]: # type: ignore
        '''
        Getting navigation status

        file:///Users/hammerchu/Downloads/user_api(1).html#当前进行中任务进度
        '''
        message = {
            "op": "subscribe",
            "topic": "/run_management/task_progress",
            "type":"std_msgs/Float64" 
        }
        try:
            resp = await self.send_data_ws(message)
            # print(f' resp : { resp} ')
            if resp and resp['msg']:
                progress = resp['msg']['data']
                return progress
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}, {resp}')
                return None

        except Exception as e:
            logging.error(e)
            return None


    async def get_nav_localization(self) -> Union[bool, None]: # type: ignore
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#导航定位状态
        '''
        message = {   
            "op": "subscribe",
            "topic": "/localization_lost",
            "type":"std_msgs/Bool" 
        }
        try:
            resp = await self.send_data_ws(message)
            print(f'NAV localization resp : { resp} ')
            if resp and resp['msg']['data']:
                is_get_lost = resp['msg']['data'] # true-定位丢失,false-定位准确
                return is_get_lost
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None


    async def get_bot_position(self) -> Union[List, None]: 
        '''
        topic = /odom 可用于获取机器人导航时，相对于地图原点的位置\n
        topic = /odom_raw 获取机器人相对初始点(开机启动点)的里程与位置信息\n

        file:///Users/hammerchu/Downloads/user_api(1).html#机器人位置
        '''
        message = {   
            "op": "subscribe",
            "topic": "/odom",
            "type":"nav_msgs/Odometry" 
        }
        try:
            resp = await self.send_data_ws(message)
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            if resp and resp['msg']:
                pos_x = resp['msg']['pose']['pose']['position']['x']
                pos_y = resp['msg']['pose']['pose']['position']['y']
                pos_z = resp['msg']['pose']['pose']['position']['z']
                ori_x = resp['msg']['pose']['pose']['orientation']['x']
                ori_y = resp['msg']['pose']['pose']['orientation']['y']
                ori_z = resp['msg']['pose']['pose']['orientation']['z'] 
                ori_w = resp['msg']['pose']['pose']['orientation']['w'] 
                
                return [pos_x, pos_y, pos_z, ori_x, ori_y, ori_z, ori_w]
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None


    async def pause_restart_nav(self, is_pause=True) -> Union[bool, None]:
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#暂停恢复当前导航任务
        '''
        if is_pause:
            key =  True 
        else:
            key =  False

        message = {
            "op": "call_service",
            "service": "/run_management/pause",
            "type": "actionlib_msgs/GoalID",
            "args":{     
                "pause": key, #true:暂停 ,false:恢复
                "reason": 0
            }
        }

        try:
            resp = await self.send_data_ws(message)
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            if resp and resp['value']['success']:
                is_success = resp['value']['success'] 
                return is_success
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None
    
    async def nav_action(self, map_name, action):
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#启动关闭导航

        Map_name: name of map to run action on
        Action: start, stop, cancel, pause, continue\n

        '''
        if action not in ['start', 'stop', 'cancel', 'pause', 'continue']:
            logging.error(f'Incorrect Nav operation action {action}')
            return None
       
        message = {
            "op": "call_service",
            "service": "/input/op",
            "type":"tools_msgs/input",
            "args": {
                "file_name": map_name, 
                "op_type": action, # start, stop, cancel, pause, continue
                "id_type":"navigation" # or waypoint for route-nav
            }
        }

        try:
            resp = await self.send_data_ws(message)
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            if resp and resp['value']['success'] :
                is_success = resp['value']['success'] 
                return is_success
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            logging.error(e)
            return None

    async def run_task_on_current_map(self, position=(0,0,0)):
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#对当前导航的地图执行实时任务

        Position -> x, y, theta
        '''

        # task_name = f"{datetime.now().strftime('%Y:%m:%d:%H:%M:%S')}{map_name}"
        message = {
            "loopTime": 1, 
            "points": [{ 
                "position": {
                    "x": position[0],
                    "y": position[1],
                    "theta": position[2]
                },
                "isNew": False,
                "cpx": 0,
                "cpy": 0
            }],
            "mode": ""
        }

        try:
            headers = {
            'Authorization': 'MTY3NTg0Njk2NC4xMjk1NjgzJDdmOGEzOTIzNTJmZTAxYzFkOGQ4ZDc1ZTdmMTYzMjBkN2FjNGE0NjM='
            }
   
            resp = self.send_data_http("apiUrl/set_task", "post", header=headers, data=message)
            if resp:                
                if resp['code']: # 0即表示成功,-1表示失败
                    return True
                else:
                    return False
            else:
                return None            

        except Exception as e:
            logging.error(e)
            return None

    async def set_obstacle_avoid_mode(self, walk_around:bool=True) -> Union[bool, None]: # type: ignore
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#设置避障模式
        '''
        if walk_around:
            key =  True 
        else:
            key =  False

        message = {
            "op": "call_service",
            "service": "/run_management/switch_obstacle_avoid_model",
            "type": "std_srvs/SetBool",
            "args":{     
                "data": key #true:避障 ,false:停障
            }
        }

        try:
            resp = await self.send_data_ws(message)
            # loop = asyncio.get_event_loop()
            # resp = loop.run_until_complete(self.send_data_ws(message))
            # loop.close()
            if resp and resp['value']['success']:
                is_success = resp['value']['success'] 
                return is_success
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None
        
        except Exception as e:
            logging.error(e)
            return None



    async def cmd_vel(self, linear_x:float=0.0, angular_x:float=0.0) -> Union[bool, None]:
        '''
        Drive the bot;\n

        linear_x > 0 -> moving forward\n
        angular_x > 0 -> turn left
        '''
        message = {
            "op":"publish",
            "topic": "/cmd_vel",
            "type": "geometry_msgs/Twist",
            "msg":{
                "linear": {
                    "x": linear_x,
                    "y": 0,
                    "z": 0
                },
                "angular": {
                    "x": angular_x,
                    "y": 0,
                    "z": 0
                }
            }
        }
        try:
            await self.send_data_ws_no_resp(message)
        except Exception as e:
            logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
            return None


    
    async def lighting(self):
        '''
        Control lighting 
        '''
        message = {
            "op":"publish",
            "topic": "/scout_light_control",
            "type": "scout_msgs/ScoutLightCmd",
            "msg": {
                "enable_cmd_light_control": "true" ,
                "front_mode": 1,
                "front_custom_value": 100,
                "rear_mode": 0,
                "rear_custom_value": 0
            }
        }
        try:
            resp = await self.send_data_ws_no_resp(message)
            if resp:
                return resp
            else:
                logging.error(f'Failed to run {sys._getframe().f_code.co_name}')
                return None

        except Exception as e:
            return f'Error - {e}'
    






async def batch_run(function, label:str):
    tasks = []
    labels = ['A', 'B', 'C', 'D', 'E']
    for i in range(5):
        tasks.append( create_task(function(labels[i]) ) )
    
    await sleep(1)
    logging.debug("now gathering tasks")
    result = await (gather(*tasks))
    logging.debug('result: ', result)


async def batch_run_forever(function, label:str):
    tasks = []
    index = 0
    labels = ['A', 'B', 'C', 'D', 'E']
    for i in range(5):
        create_task(function(labels[i]) ) 
    
    while index < 20:
        await sleep(1)
        logging.debug('timer: ', index)
        index += 1




if __name__ == '__main__':

    print('Running main')

    app = Connect('192.168.1.102')
    # r = asyncio.run(app.get_nav_status())
    app.get_nav_status()
    
    # print(r)

    # asyncio.run(app.lighting())





    '''Run in parallel '''
    # run(batch_run_forever(app.get_bot_status, ''))


    '''Run in parallel and in batch'''
    # run(batch_run(app.get_bot_status, ''))
    '''
    A launched
    B launched
    C launched
    D launched
    E launched
    B done after 0.15156074475310144s
    A done after 0.3988251512623253s
    C done after 0.980109410083761s
    now gathering tasks
    E done after 2.3564309284208345s
    D done after 3.226522373257637s
    result:  ['A_0.3988251512623253', 'B_0.15156074475310144', 'C_0.980109410083761', 'D_3.226522373257637', 'E_2.3564309284208345']
    '''



    '''Run in sequenial'''
    # for i in range(5):
    #     label = ['A', 'B', 'C', 'D', 'E']
    #     print(asyncio.run(app.get_bot_status(label[i])))

    '''
    A launched
    A done after 2.9623588532212093s
    A_2.9623588532212093
    B launched
    B done after 3.5356719128189216s
    B_3.5356719128189216
    C launched
    C done after 1.4789386123539967s
    C_1.4789386123539967
    D launched
    D done after 0.45401467940840656s
    D_0.45401467940840656
    E launched
    E done after 4.419964332363838s
    E_4.419964332363838
    '''
    
    '''run in parallel and in batch'''
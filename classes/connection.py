#-*-coding:utf-8-*-
from typing import Tuple, List, Dict
from urllib import response
import requests
import asyncio
import websockets
from asyncio import create_task, gather, sleep, run
import random
import time
import json, logging


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.WARNING)

class Connect():
    '''
    Functionalities for all the key websocket connection requests with the agileX bots
    Manged by async send and feedback queues
    '''


    def __init__(self, bot_ip):
        self.bot_ip = bot_ip
        self.queue = asyncio.Queue()

        self.finish = False

        self.auth_token = ''

        self.version = '0.0.12'

        # asyncio.run(self.run()) // error -> got Future <Future pending> attached to a different loop
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.run())

    def get_ver(self):
        print(self.version)

    async def send_data_http(self, postfix, action, header, params):
        uri = f"ws://192.168.1.102:8880/"
        if action == 'get':
            response = requests.get(uri+postfix, headers=header, params=params)
            return response.json
        elif action == 'post':
            response = requests.post(uri+postfix, headers=header, params=params)
            return response.json
        else:
            logging.error(f'Error - unknown action {action}')
            return
          
    async def send_data_ws(self, message):
        # uri = f"ws://{self.bot_ip}:9090" #填写实际的机器人IP地址:9090
        uri = f"ws://192.168.1.102:9090" #填写实际的机器人IP地址:9090
        async with websockets.connect(uri) as websocket:
        
            await websocket.send(bytes(json.dumps(message, ensure_ascii=False).encode("utf-8")))
            # response = await websocket.recv()
            # yield from asyncio.wait_for(websocket.recv(), timeout=10)
            response = asyncio.wait_for(websocket.recv(), timeout=3)
            return response
    
    async def send_data_ws_no_resp(self, message):
        # uri = f"ws://{self.bot_ip}:9090" #填写实际的机器人IP地址:9090
        uri = f"ws://192.168.1.102:9090" #填写实际的机器人IP地址:9090
        async with websockets.connect(uri) as websocket:
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
    async def login(self):
        action = 'post'
        url = f"http://{self.bot_ip}:8880/apiUrl/user/passport/login"
        headers = ""
        params = {
            "username": "agilex",
            "password": "NTdhMTE5NGNiMDczY2U4YjNiYjM2NWU0YjgwNWE5YWU="
        }
        try:
            return await self.send_data_http(url, action, headers, params)
        except Exception as e:
            logging.error(e)
            return None
        
    async def get_dev_ver(self):
        action = 'get'
        url = f"http://{self.bot_ip}:8880/apiUrl/dev_version"
        headers = { "Authorization" : self.auth_token }
        params = ""
        try:
            return await self.send_data_http(url, action, headers, params)
        except Exception as e:
            logging.error(e)
            return None
    
    async def get_maps(self):
        action = 'post'
        sort_type = 'time'
        is_reverse = ''
        url = f"http://{self.bot_ip}:8880/apiUrl/map_list?page=1&limit=-1&sortType={sort_type}&reverse={is_reverse}"
        headers = { "Authorization" : self.auth_token }
        params = ""
        try:
            return await self.send_data_http(url, action, headers, params)
        except Exception as e:
            logging.error(e)
            return None




    '''
    websocket functions
    '''
    
    async def get_sensor_status(self) -> Tuple[str, str, str] | None:
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
            resp = json.loads(resp) # type: ignore
            RTK_status = resp['msg']['RTK_status']
            lidar_status = resp['msg']['lidar_status']
            camera_status = resp['msg']['camera_status']

            return (RTK_status, lidar_status, camera_status)

        except Exception as e:
            logging.error(e)
            return None
    

    async def get_rtk_data(self) -> Tuple[str, str, str] | bool: # type: ignore
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
            resp = await self.send_data_ws(message)
            resp = json.loads(resp) # type: ignore
            status = resp['msg']['nav']
            name = resp['msg']['name']
            task = resp['msg']['task']
            return (status, name, task)

        except Exception as e:
            logging.error(e)
            return None
    

    async def get_nav_status(self) -> bool | None:
        '''
        Return True if bot's nav mode is ON
        '''
        message = {
            "op":"subscribe",
            "topic": "/slam_status",
            "type": "tools_msgs/slamStatus"
        }
        try:
            resp = await self.send_data_ws(message)
            resp = json.loads(resp) # type: ignore
            nav_status = resp['msg']['nav']['state']
            return nav_status
            
        except Exception as e:
            logging.error(e)
            return None
        

    async def start_nav(self) -> bool | None: # type: ignore
        '''
        file:///Users/hammerchu/Downloads/user_api(1).html#启动关闭导航
        '''
        message = {
            "op": "call_service",
            "service": "/input/op",
            "type":"tools_msgs/input",
            "args": {
                "file_name": "",
                "op_type":"start",
                "id_type":"follow_line"
            }
        }
        try:
            resp = await self.send_data_ws(message)
            resp = json.loads(resp)
            is_success = resp['value']['success'] 
            
            return is_success

        except Exception as e:
            logging.error(e)
            return None


    async def get_navi_status(self) -> Tuple[str, str, str] | None: # type: ignore
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
            resp = json.loads(resp)
            status = resp['msg']['status'] # e.g. 1 : 正在执行任务
            map_name = resp['msg']['map_name']
            text = resp['msg']['text']
            return (status, map_name, text)

        except Exception as e:
            logging.error(e)
            return None
    

    async def get_navi_path(self) -> List[Dict] | bool: # type: ignore
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
            resp = json.loads(resp)
            path = resp['msg']['poses']

            return path

        except Exception as e:
            logging.error(e)
            return None


    async def get_nav_progress(self) -> float | bool: # type: ignore
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
            resp = json.loads(resp)
            progress = resp['msg']['data']
            
            return progress

        except Exception as e:
            logging.error(e)
            return None


    async def get_nav_localization(self) -> bool | None: # type: ignore
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
            resp = json.loads(resp)
            is_get_lost = resp['msg']['data'] # true-定位丢失,false-定位准确
            
            return is_get_lost

        except Exception as e:
            logging.error(e)
            return None


    async def pause_restart_nav(self, is_pause=True) -> bool | None: # type: ignore
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
            resp = json.loads(resp)
            is_success = resp['value']['success'] 
            
            return is_success

        except Exception as e:
            logging.error(e)
            return None
    
    
    async def set_obstacle_avoid_mode(self, walk_around:bool=True) -> bool | None: # type: ignore
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
            resp = json.loads(resp)
            is_success = resp['value']['success'] 
            
            return is_success

        except Exception as e:
            logging.error(e)
            return None



    async def cmd_vel(self, linear_x:float=0.0, angular_x:float=0.0) -> bool | None:
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
            resp = await self.send_data_ws_no_resp(message)
            return True
        except Exception as e:
            return None


    async def stop(self):
        message = {
            "op":"publish",
            "topic": "/cmd_vel",
            "type": "geometry_msgs/Twist",
            "msg":{
                "linear": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "angular": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                }
            }
        }
        try:
            return await self.send_data_ws_no_resp(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'
    
    async def lighting(self):
        message = {
            "op":"publish",
            "topic": "/scout_light_control",
            "type": "scout_msgs/ScoutLightCmd",
            "msg": {
                "enable_cmd_light_control": "true" ,
                "front_mode": 3,
                "front_custom_value": 100,
                "rear_mode": 0,
                "rear_custom_value": 0
            }
        }
        try:
            return await self.send_data_ws_no_resp(message)
            # return await self.mock_send_data(message)
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

    app = Connect('192.168.1.1')

    app.lighting()





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
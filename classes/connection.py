#-*-coding:utf-8-*-
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

'''
Class 
'''
class ConnectWS():
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
                return False
        
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
            return f'Error - {e}'
        
    async def get_dev_ver(self):
        action = 'get'
        url = f"http://{self.bot_ip}:8880/apiUrl/dev_version"
        headers = { "Authorization" : self.auth_token }
        params = ""
        try:
            return await self.send_data_http(url, action, headers, params)
        except Exception as e:
            return f'Error - {e}'
    
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
            return f'Error - {e}'

    '''
    websocket functions
    '''
    async def get_bot_status(self):
        message = {
            "op":"subscribe",
            "topic": "/slam_status",
            "type": "tools_msgs/slamStatus"
        }
        # result = await create_task(self.mock_send_data('get_bot_status'))
        # return await self.send_data_ws(message)
        try:
            return await self.send_data_ws(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'

    async def get_sensor_status(self):
        message = {
            "op":"subscribe",
            "topic": "/sensor_status",
            "type": "tools_msgs/SensorStatus"
        }

        try:
            return await self.send_data_ws(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'
    
    async def test_function(self, value):
        message = {
            "op":"subscribe",
            "topic": f"/{value}",
            "type": f"test/test"
        }

        print(f'test function  - {message}')
        return 1 # type: ignore

    async def get_rtk_data(self):
        message = {
            "op":"subscribe",
            "topic": "/gnss_status",
            "type": "tools_msgs/GnssStatus"
        }
        try:
            return await self.send_data_ws(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'

    async def up(self, value=1):
        message = {
            "op":"publish",
            "topic": "/cmd_vel",
            "type": "geometry_msgs/Twist",
            "msg":{
                "linear": {
                    "x": value,
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
        print(f'up: {message}')
        try:
            return await self.send_data_ws_no_resp(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'
        
    
    async def down(self, value=1):
        message = {
            "op":"publish",
            "topic": "/cmd_vel",
            "type": "geometry_msgs/Twist",
            "msg":{
                "linear": {
                    "x": -1 * value,
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
        print(f'down: {message}')
        try:
            return await self.send_data_ws_no_resp(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'

    async def left(self, value=1):
        message = {
            "op":"publish",
            "topic": "/cmd_vel",
            "type": "geometry_msgs/Twist",
            "msg":{
                "linear": {
                    "x": 1 * value,
                    "y": 0,
                    "z": 0
                },
                "angular": {
                    "x": 0,
                    "y": 0,
                    "z": 1 * value,
                }
            }
        }
        print(f'left: {message}')
        try:
            return await self.send_data_ws_no_resp(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'
    
    async def right(self, value=1):
        message = {
            "op":"publish",
            "topic": "/cmd_vel",
            "type": "geometry_msgs/Twist",
            "msg":{
                "linear": {
                    "x": 1 * value,
                    "y": 0,
                    "z": 0
                },
                "angular": {
                    "x": 0,
                    "y": 0,
                    "z": -1 * value,
                }
            }
        }
        print(f'right: {message}')
        try:
            return await self.send_data_ws_no_resp(message)
            # return await self.mock_send_data(message)
        except Exception as e:
            return f'Error - {e}'
    
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
    
    async def get_rtk_data(self):
        message = {
            "op":"subscribe",
            "topic": "/gnss_status",
            "type": "tools_msgs/GnssStatus"
        }
        try:
            return await self.send_data_ws(message)
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

    app = ConnectWS('192.168.1.1')

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
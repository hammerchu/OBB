#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file presents an interface for interacting with the Playstation 4 Controller
# in Python. Simply plug your PS4 controller into your computer using USB and run this
# script!
#
# NOTE: I assume in this script that the only joystick plugged in is the PS4 controller.
#       if this is not the case, you will need to change the class accordingly.
#
# Copyright © 2015 Clay L. McLeod <clay.l.mcleod@gmail.com>
#
# Distributed under terms of the MIT license.

import os
import pprint
import pygame
import time
from threading import Thread
from bot.classes.connection import Connect

import asyncio

class DS4(object):
    """Class representing the PS4 controller. Pretty straightforward functionality.
    
    self.button_labels = {
            '0':'cross',
            '1':'circle',
            '2':'square',
            '3':'triangle',

            '4':'share',
            '5':'logo',
            '6':'options',
            '7':'left_hat_press',
            '8':'right_hat_press',
            '9':'L1',
            '10':'R1',

            '11':'up',
            '12':'down',
            '13':'left',
            '14':'right',
        }
    self.hat_label = {
        '0':'left_hat_x',
        '1':'left_hat_y',
        '2':'right_hat_x',
        '3':'right_hat_y',

        '4':'L2',
        '5':'R2',
    }
    
    """

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        """Initialize the joystick components"""
        print('\nrunning init\n')
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.connect = True

        self.running = True
        self.debug = True

        self.speed_factor = 1
        self.linear_x = -1
        self.angular_x = -1

        self.button_labels = {
            '0':'cross',
            '1':'circle',
            '2':'square',
            '3':'triangle',

            '4':'share',
            '5':'logo',
            '6':'options',
            '7':'left_hat_press',
            '8':'right_hat_press',
            '9':'L1',
            '10':'R1',

            '11':'up',
            '12':'down',
            '13':'left',
            '14':'right',
        }
        self.hat_label = {
            '0':'left_hat_x',
            '1':'left_hat_y',
            '2':'right_hat_x',
            '3':'right_hat_y',

            '4':'L2',
            '5':'R2',
        }
  
        if self.connect:
            self.connect_to_bot()
        listen_thread = Thread(target=self.listen_wraper).start()
    

    def connect_to_bot(self):
        self.conn = Connect('192.168.1.102')

    def listen_wraper(self):
        asyncio.run(self.listen())

    async def listen(self):
        """Listen for events to happen"""
        if self.controller:
            if not self.axis_data:
                self.axis_data = {}

            if not self.button_data:
                self.button_data = {}
                for i in range(self.controller.get_numbuttons()):
                    self.button_data[i] = False

            if not self.hat_data:
                self.hat_data = {}
                for i in range(self.controller.get_numhats()):
                    self.hat_data[i] = (0, 0)

        fps = -1
        while self.running:
            then = time.time()
            if self.axis_data is not None and self.button_data is not None and self.hat_data is not None:
                for event in pygame.event.get():
                    if event.type == pygame.JOYAXISMOTION:
                        # self.axis_data[1] = 0
                        # self.axis_data[2] = 0
                        self.axis_data[event.axis] = round(event.value,2)
                    elif event.type == pygame.JOYBUTTONDOWN:
                        self.button_data[event.button] = True
                    elif event.type == pygame.JOYBUTTONUP:
                        self.button_data[event.button] = False
                    elif event.type == pygame.JOYHATMOTION:
                        self.hat_data[event.hat] = event.value

            
                    if self.debug:
                        os.system('clear')

                        pprint.pprint(f'B {self.button_data}')

                        for idx, k in enumerate(self.axis_data.values()):
                            pprint.pprint(f'{idx} {k}')

                        pprint.pprint(f'A {self.axis_data}')
                        # pprint.pprint(self.hat_data)
                        pprint.pprint(f'H {self.hat_data}')
                        # await self.cmd_vel()
                        if self.connect:
                            await self.cmd_vel()
                        try:
                            if self.button_data and self.button_data[10] == True:
                                self.speed_factor = 0.5
                            elif self.button_data and self.button_data[9] == True:
                                self.speed_factor = 2
                            else:
                                self.speed_factor = 1
                        except:
                            pass
                        pprint.pprint(f'S {(self.speed_factor)}')

                        pprint.pprint(f'vel {(self.linear_x, self.angular_x)}')

                        pprint.pprint(fps)


                    if self.button_data[4] == True:
                        self.running = False


            now = time.time()
            fps = 1/(now - then )
            fps += 1
            # time.sleep(1/30)


    async def cmd_vel(self):
        '''
        Submit vel instruction to BOT
        '''
        hat_thread = 0.1
        is_stopped = False

        try:
            if self.axis_data and self.axis_data[1]:
                # print('self.linear_x', self.hat_data[1])
                if -1 * hat_thread < self.axis_data[1] < hat_thread:
                    self.linear_x = 0
                else:
                    self.linear_x = -1 * self.axis_data[1]* self.speed_factor 
            if self.axis_data and self.axis_data[2]:
                if -1 * hat_thread < self.axis_data[2] < hat_thread:
                    self.angular_x = 0
                else:
                    self.angular_x = -1 * self.axis_data[2] * self.speed_factor 
            
            if self.linear_x != 0 or self.angular_x != 0:
                await self.conn.cmd_vel(self.linear_x, self.angular_x)
                is_stopped = False
            elif self.linear_x == 0 or self.angular_x == 0 and not is_stopped:
                await self.conn.cmd_vel(self.linear_x, self.angular_x)
                is_stopped = True
            elif self.linear_x == 0 or self.angular_x == 0 and is_stopped:
                pass


        except KeyError as e:
            self.angular_x = 99
            print('error', e)


if __name__ == "__main__":
    ps4 = DS4()
    ps4.init()
    



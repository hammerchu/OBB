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

class PS4Controller(object):
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
        
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.conn = Connect('192.168.1.102')

        self.running = True
        self.debug = True

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
        listen_thread = Thread(target=self.listen).run()



    def listen(self):
        """Listen for events to happen"""
        
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

        ready_to_quit = False
        fps = -1
        while self.running:
            then = time.time()
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = round(event.value,2)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value

                # Insert your code on what you would like to happen for each event here!
                # In the current setup, I have the state simply printing out to the screen.
                
                if self.debug:
                    os.system('clear')
                    pprint.pprint(self.button_data)
                    pprint.pprint(self.axis_data)
                    pprint.pprint(self.hat_data)
                    pprint.pprint(fps)

                

                if self.button_data[4] == True:
                    self.running = False


            now = time.time()
            fps = 1/(now - then )


    async def cmd_vel(self):
        '''
        Submit vel instruction to BOT
        '''
        hat_thread = 0.1
        if self.hat_data:
            if -1 * hat_thread < self.hat_data[1] < hat_thread:
                linear_x = self.hat_data[1]
            else:
                linear_x = 0
            if -1 * hat_thread < self.hat_data[2] < hat_thread:
                angular_x = self.hat_data[2]
            else:
                angular_x = 0
                
            await self.conn.cmd_vel(linear_x, angular_x)



if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    # ps4.listen()


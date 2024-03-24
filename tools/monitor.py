import tkinter as tk
from tkinter import messagebox, StringVar
from tkinter import ttk
from datetime import datetime
import asyncio
import time
from threading import Thread
from turtle import bgcolor
from bot.classes.connection import Connect
from bot.classes.navigate import Navigate
from bot.tools.utilities import get_scaled_control_map_color
from bot.tools.joystick import DS4
import logging

# load_connection = True
# load_controller = False

logging.basicConfig(level=logging.INFO)

class Monitor:

    def __init__(self, nav, load_connection=True, load_controller=True ):
        self.window = tk.Tk()
        self.window.title("OBB Testing")
        self.window.geometry("400x860")

        self.FONT_COLOR = '#cccccc'

        self.nav_code_label = {
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

        self.running = True

        self.ui()

        if load_connection:
            try:

                # nav = asyncio.run( Navigate._init_()) # coming from inoput instead
                self.nav = nav
                # conn = self.nav.connection
                r = self.nav.connection.login()
                if r:
                    auth_token = r
                else:
                    output = f'Unable to obtain API token'
                    auth_token = ''
                r = self.nav.connection.get_maps_list()
                print(r)
            except Exception as e:
                logging.warning("Unable to connect to BOT: ", e)

        if load_controller:  
            controller = DS4()
            controller.init()

        # Run the update loop
        update_thread = Thread(target=self.update_loops)
        update_thread.start()
        timer_thread = Thread(target=self.timer)
        timer_thread.start()

        # Start the GUI event loop
        self.window.mainloop()


    def ui(self):
        self.is_nav_on = StringVar()
        self.is_nav_on.set(self.FONT_COLOR)
        # current_map = StringVar()
        # current_map.set('unknown')
        self.current_task =  StringVar()
        self.current_task.set('unknown')
        self.nav_code = StringVar()
        self.nav_code.set('unknown')
        self.nav_progress = StringVar()
        self.nav_progress.set(str(0))
        self.position = StringVar()
        self.position.set(str((-1, -1, -1)))
        self.orientation = StringVar()
        self.orientation.set(str((-1, -1, -1, -1)))
        self.control_map_color = StringVar()
        self.control_map_color.set(str((0, 0, 0, 0)))
        self.vel = StringVar()
        self.vel.set(str((-1, -1)))

        self.titles = [
            # 'Current map', 
            'Current task', 
            'Nav progress',
            'Nav Code', 
            'Position', 
            'Orientation', 
            'Control Map Color',
            'vel'
            ]
        
        self.vars = [
            # current_map, 
            self.current_task, 
            self.nav_progress, 
            self.nav_code, 
            self.position,
            self.orientation, 
            self.control_map_color,
            self.vel
            ]
        ''' UI '''

        # Bind space bar key press event to the function
        # window.bind("<space>", space_bar_pressed)
        # window.bind("<space>", switch_page)

        self.count_var = StringVar()
        self.output_var = StringVar()
        self.count_var.set(str(0))
        self.output_var.set('')

        tabControl = ttk.Notebook(self.window) 
        tab1 = ttk.Frame(tabControl, width=390, height=90)

        tab2 = ttk.Frame(tabControl, width=390, height=90) 
        tab3 = ttk.Frame(tabControl, width=390, height=90) 
        
        tabControl.add(tab3, text ='    Bring up    ') 
        tabControl.add(tab2, text ='    Task    ') 
        tabControl.add(tab1, text ='    Info    ') 
        tabControl.pack(expand = 1, fill ="both") 


        '''
        TAB 1
        '''

        self.content_label_list = []
        # card_stack_frame_p1 = tk.Frame(tab1, bg="white", width=390, height=240, padx=5, pady=5)
        # card_stack_frame_p1.pack(padx=5, pady=5)

        for i, title in enumerate(self.titles):

            # Create the title label
            title_label = tk.Label(tab1, text=title, font=("Arial", 12, "bold"), fg=self.FONT_COLOR, bg='systemTransparent')
            title_label.pack(side=tk.TOP, padx=5, pady=2)


            # Create the content label
            content_label = tk.Label(tab1, textvariable=self.vars[i], font=("Arial", 26), bg='systemTransparent')
            content_label.pack(side=tk.TOP, padx=5, pady=5)
            self.content_label_list.append(content_label)

            # Create the title label
            space = tk.Label(tab1, text='', font=("Arial", 12, "bold"), bg='systemTransparent')
            space.pack(side=tk.TOP, padx=5, pady=3)

            # # Create a small label in the left upper corner
            small_label = tk.Label(self.window, textvariable=self.count_var, font=("Arial", 14))
            small_label.place(x=5, y=5)

        close_button = tk.Button(tab1, text=f"Close", command=lambda: self.close_window(), width=80, height=30)
        close_button.pack(side=tk.BOTTOM, padx=5, pady=5)


        '''
        TAB 2
        '''
        label_1 = tk.Label(tab2, text="Travel to station", font=("Arial", 14), bg='systemTransparent')
        label_1.pack(side=tk.TOP, padx=5, pady=3)

        map_name_entry_field_1 = tk.Entry(tab2, width=80)
        map_name_entry_field_1.insert(0, f"Elements05") 
        map_name_entry_field_1.pack(side=tk.TOP, padx=5, pady=5)

        task_name_entry_field_1 = tk.Entry(tab2, width=80)
        task_name_entry_field_1.insert(0, f"station_name") 
        task_name_entry_field_1.pack(side=tk.TOP, padx=5, pady=5)

        submit_button_1 = tk.Button(tab2, text=f"Travel to station", command=lambda: self.goto_station(map_name_entry_field_1, task_name_entry_field_1), width=80)
        submit_button_1.pack(side=tk.TOP, padx=5, pady=5)

        space = tk.Label(tab2, text='', font=("Arial", 12, "bold"), bg='systemTransparent')
        space.pack(side=tk.TOP, padx=5, pady=3)


        label_2 = tk.Label(tab2, text="Run task", font=("Arial", 14), bg='systemTransparent')
        label_2.pack(side=tk.TOP, padx=5, pady=3)

        map_name_entry_field_2 = tk.Entry(tab2, width=80)
        map_name_entry_field_2.insert(0, f"Elements05") 
        map_name_entry_field_2.pack(side=tk.TOP, padx=5, pady=5)

        task_name_entry_field_2 = tk.Entry(tab2, width=80)
        task_name_entry_field_2.insert(0, f" task_name") 
        task_name_entry_field_2.pack(side=tk.TOP, padx=5, pady=5)

        submit_button_2 = tk.Button(tab2, text=f"Run task on map", command=lambda: self.run_task(map_name_entry_field_2, task_name_entry_field_2), width=80)
        submit_button_2.pack(side=tk.TOP, padx=5, pady=5)

        space = tk.Label(tab2, text='', font=("Arial", 12, "bold"), bg='systemTransparent')
        space.pack(side=tk.TOP, padx=5, pady=3)

        '''
        TAB 3
        '''
        label_3 = tk.Label(tab3, text="Current map", font=("Arial", 14), bg='systemTransparent')
        label_3.pack(side=tk.TOP, padx=5, pady=3)

        map_name_entry_field_3 = tk.Entry(tab3, width=80)
        map_name_entry_field_3.insert(0, f"Elements05") 
        map_name_entry_field_3.pack(side=tk.TOP, padx=5, pady=5)

        submit_button_3 = tk.Button(tab3, text=f"Submit current map", command=lambda: self.set_current_map(map_name_entry_field_3), width=80)
        submit_button_3.pack(side=tk.TOP, padx=5, pady=5)

        submit_button_toggle_nav = tk.Button(tab3, text=f" Nav On", command=lambda: self.toggle_nav(map_name_entry_field_3, 'start'), width=80)
        submit_button_toggle_nav.pack(side=tk.TOP, padx=5, pady=5)

        submit_button_toggle_nav = tk.Button(tab3, text=f" Nav Off", command=lambda: self.toggle_nav(map_name_entry_field_3, 'stop'), width=80)
        submit_button_toggle_nav.pack(side=tk.TOP, padx=5, pady=5)


        ''' Message box '''
        # Create a frame for the message box
        message_box_frame = tk.Frame(tab2, bg="light grey", bd=1, relief=tk.SOLID, width=390, height=50, padx=5, pady=5)
        message_box_frame.pack(side=tk.BOTTOM, padx=5, pady=5)


        # Create the message label
        message_label = tk.Label(message_box_frame, textvariable=self.output_var, font=("Arial", 14), width=390, height=50)
        message_label.pack()

        close_button = tk.Button(tab2, text=f"Close", command=lambda: self.close_window(), width=80, height=30)
        close_button.pack(side=tk.BOTTOM, padx=5, pady=5)


    def close_window(self):
        # with open('log', 'a+') as log_file:

        #     log_file.write(f'\n<section closed at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}>')
        #     log_file.write('\n')
        #     # log_file.write(outputs)
        self.running = False
        # update_thread.join()
        # timer_thread.join()
        self.window.destroy()


    def timer(self):
        count = 0
        while self.running:
            # print(f'# {count}')
            count += 1 
            time.sleep(1)


    def update_loops(self):
        # global is_nav_on
        # global nav_code
        # global nav_progress
        # global position
        # global orientation
        # global current_map
        # global current_task
        # global FONT_COLOR
        # global count_var
        # global output_var
        # global title_label

        current_map_name = ''
        current_map_position = (-1, -1)
        counter = 0
        while self.running:
            # new_loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(new_loop)
            # loop = asyncio.get_event_loop()
            try:
                
                print(f'-- get_nav_status : { self.nav.nav_status} \n')
                if self.nav.nav_status:
                    # if is_nav_on is ON
                    self.FONT_COLOR = 'black'
                else:
                    self.FONT_COLOR = 'red'
                for c in self.content_label_list:
                    c.config(fg=self.FONT_COLOR)

                # if nav.current_map:
                #     # current_map_name=r[1]
                #     current_map.set(nav.current_map)
                # else:
                #     current_map.set('unknown')

                if self.nav.current_map and self.nav.current_task:
                    self.current_task.set(f'{self.nav.current_task} @ {self.nav.current_map}' )
                else:
                    self.current_task.set('unknown')
                

                logging.debug(f'-- get_navi_code : { self.nav.code } - {self.nav_code_label[(str(nav.code))]}\n')
                if self.nav.code is not None:
                    self.nav_code.set(f'{self.nav_code_label[(str(self.nav.code))]}')
                else:
                    self.nav_code.set('-----')            


                if self.nav.progress is not None:
                    self.nav_progress.set(str(self.nav.progress))
                else:
                    self.nav_progress.set('-----')
                
                
                logging.debug(f'-- get_bot_position : { self.nav.px}, {self.nav.py} ')
                if self.nav.px is not None and self.nav.py is not None and self.nav.py is not None and self.nav.ox is not None and self.nav.oy is not None and self.nav.oz is not None and self.nav.ow is not None:
                    current_map_position = (self.nav.px, self.nav.py)
                    self.position.set(str(   round(self.nav.px, 2),  round(self.nav.py, 2)  ))
                    self.orientation.set(str(    (round(self.nav.ox, 2), round(self.nav.oy, 2),round(self.nav.oz, 2),round(self.nav.ow, 2))  ))


                    self.control_map_color.set(str(self.nav.control_map_color)) 

                logging.debug(f'\n -- get CONTROL COLOR : { self.nav.control_map_color} --- \n')

                # loop.close()
            except Exception as e:
                self.output_var.set(str(e))

        
            # nav_progress += 1
            counter+=1
            self.count_var.set(str(counter))

            time.sleep(60/30)


    def goto_station(self, map, station):
        print(f'\n >>>>> Goto map : { map.get()} - station : {station.get()}')
        # Travel to any stations(if they connect to the current map)
        dest_map = map.get()
        dest_station = station.get()
        self.nav.travel_to_station(dest_map, dest_station, None)


    def run_task(self, map, task):
        print(f'\n >>>>> Run task : {task.get()} on map : { map.get()}')
        # Run a preset task on a map
        self.nav.connection.run_list_task(map.get(), task.get())

    def set_current_map(self, map_field):
        if map_field !='':
            print(f'>>>>> Set current map to {map_field.get()}')
            self.nav.current_map = map_field.get()
        else:
            messagebox.showinfo("Error",  "Current map cannot be empty") 

    def toggle_nav(self, map_field, action):
        asyncio.run(self.nav.nav_action(map_field.get(), action))


if __name__ == '__main__':

    # nav = asyncio.run( Navigate._init_()) # coming from inoput instead
    win = Monitor(nav=None, load_connection=False, load_controller=False )
















    
    
    

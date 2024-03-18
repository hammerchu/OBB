import tkinter as tk
from tkinter import *
from tkinter import ttk
from datetime import datetime
import asyncio
import time
from threading import Thread
from turtle import bgcolor
from bot.classes.connection import Connect
from bot.classes.navigate import Navigate
from bot.tools.utilities import get_scaled_control_map_color
from bot.tools.joystick import PS4Controller
import logging

testing_ui = True

logging.basicConfig(level=logging.INFO)


window = tk.Tk()
window.title("OBB Testing")
window.geometry("400x860")

FONT_COLOR = '#cccccc'

if not testing_ui:
    ps4 = PS4Controller()
    ps4.init()

    nav = Navigate()
    conn = nav.connection
    r = conn.login()
    if r:
        auth_token = r
    else:
        output = f'Unable to obtain API token'
        auth_token = ''
    r = conn.get_maps_list()
    print(r)
    # conn.start_nav()
   

current_page = 0
total_page = 2

is_nav_on = StringVar()
is_nav_on.set(FONT_COLOR)
current_map = StringVar()
current_map.set('unknown')
current_task =  StringVar()
current_task.set('unknown')
nav_code = StringVar()
nav_code.set('unknown')
nav_progress = StringVar()
nav_progress.set(str(0))
position = StringVar()
position.set(str((-1, -1, -1)))
orientation = StringVar()
orientation.set(str((-1, -1, -1, -1)))
control_map_color = StringVar()
control_map_color.set(str((0, 0, 0, 0)))

running = True



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

titles = [
    'Current map', 
    'Current task', 
    'Nav progress',
    'Nav Code', 
    'Position', 
    'Orientation', 
    'Control Map Color'
    ]
vars = [
    current_map, 
    current_task, 
    nav_progress, 
    nav_code, 
    position,
    orientation, 
    control_map_color
    ]





def close_window():
    # with open('log', 'a+') as log_file:

    #     log_file.write(f'\n<section closed at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}>')
    #     log_file.write('\n')
    #     # log_file.write(outputs)
    global running 
    running = False
    # update_thread.join()
    # timer_thread.join()
    window.destroy()



# Function to handle space bar key press
async def space_bar_pressed(event):
    # Perform your desired actions here
    print("Space bar pressed")
    change_background_color()
    # asyncio.run(conn.cmd_vel())



def timer():
    count = 0
    while running:
        print(f'# {count}')
        count += 1 
        time.sleep(1)

def update_loops():
    global is_nav_on
    global nav_code
    global nav_progress
    global position
    global orientation
    global current_map
    global current_task
    global FONT_COLOR
    global count_var
    global output_var
    global title_label

    current_map_name = ''
    current_map_position = (-1, -1)
    counter = 0
    while running:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        try:
            
            
            nav.nav_status
            print(f' get_nav_status : { nav.nav_status} \n')
            if nav.nav_status:
                # if is_nav_on is ON
                FONT_COLOR = 'black'
            else:
                FONT_COLOR = 'red'
            for c in content_label_list:
                c.config(fg=FONT_COLOR)

            if nav.current_map:
                # current_map_name=r[1]
                current_map.set(nav.current_map)
            else:
                current_map.set('unknown')

            if nav.current_task:
                current_task.set(nav.current_task)
            else:
                current_task.set('unknown')
            

            print(f' get_navi_code : { nav.code } - {nav_code_label[(str(nav.code))]}\n')
            if nav.code is not None:
                nav_code.set(f'{nav_code_label[(str(nav.code))]}')
            else:
                nav_code.set('-----')            


            if nav.progress is not None:
                nav_progress.set(str(nav.progress))
            else:
                nav_progress.set('-----')
            
            
            print(f' get_bot_position : { nav.px}, {nav.py} ')
            if nav.px is not None and nav.py is not None:
                current_map_position = (nav.px, nav.py)
                position.set((str(nav.px).zfill(1) + ' ' + str(nav.py).zfill(1) + ' ' +  str(nav.pz).zfill(1)))
                orientation.set((str(nav.ox).zfill(1) + ' ' + str(nav.oy).zfill(1) + ' ' +  str(nav.oz).zfill(1) + ' ' +  str(nav.oz).zfill(1)))

                # if current_map_name and current_map_position != (-1, -1):
                #     color = get_scaled_control_map_color(current_map_name, current_map_position)
                # else:
                #     color = "unknown"

                print(f'\n --- CONTROL COLOR : { nav.control_map_color} --- \n')
                control_map_color.set(str(nav.control_map_color)) 

            # loop.close()
        except Exception as e:
            output_var.set(str(e))

    
        # nav_progress += 1
        counter+=1
        count_var.set(str(counter))

        time.sleep(60/30)

def update_loops_old():
    global is_nav_on
    global nav_code
    global nav_progress
    global position
    global orientation
    global current_map
    global current_task
    global FONT_COLOR
    global count_var
    global output_var
    global title_label

    current_map_name = ''
    current_map_position = (-1, -1)
    counter = 0
    while running:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        try:
            # task = asyncio.ensure_future(conn.get_nav_status())
            # r = loop.run_until_complete(task)
            r = loop.run_until_complete(asyncio.wait_for(conn.get_nav_status(), 3))
            print(f' get_nav_status : { r} \n')
            if r and r[0]:
                # if is_nav_on is ON
                FONT_COLOR = 'black'
                # FONT_COLOR = 'red'
            else:
                # FONT_COLOR = '#cccccc'
                FONT_COLOR = 'red'
            for c in content_label_list:
                c.config(fg=FONT_COLOR)

            if r and r[1]:
                current_map_name=r[1]
                current_map.set(r[1])
            else:
                current_map.set('unknown')

            if r and r[2]:
                current_task.set(r[2])
                
            else:
                current_task.set('unknown')
            
            r = loop.run_until_complete(asyncio.wait_for(conn.get_navi_code(), 0.5))
            print(f' get_navi_code : { r} - {nav_code_label[(str(r))]}\n')
            if r is not None:
                nav_code.set(f'{nav_code_label[(str(r))]}')
            else:
                nav_code.set('-----')
            # print(f' get_navi_code : { nav_code_label[(str(r))] } ')                


            r = loop.run_until_complete(asyncio.wait_for(conn.get_nav_progress(), 3))
            # print(f' get_nav_progress : { r} \n')
            if r is not None:
                nav_progress.set(str(r))
            else:
                nav_progress.set('-----')
            
            
            r = loop.run_until_complete(asyncio.wait_for(conn.get_bot_position(), 3))
            print(f' get_bot_position : { r} ')
            if r and r[0]:
                current_map_position = (r[0], r[1])
                position.set((str(r[0]).zfill(1) + ' ' + str(r[1]).zfill(1) + ' ' +  str(r[2]).zfill(1)))
                orientation.set((str(r[3]).zfill(1) + ' ' + str(r[4]).zfill(1) + ' ' +  str(r[5]).zfill(1) + ' ' +  str(r[6]).zfill(1)))

            
            if current_map_name and current_map_position != (-1, -1):
                color = get_scaled_control_map_color(current_map_name, current_map_position)
            else:
                color = "unknown"

            print(f'\n --- CONTROL COLOR : { color} --- \n')
            control_map_color.set(str(color)) 

            # loop.close()
        except Exception as e:
            output_var.set(str(e))

    
        # nav_progress += 1
        counter+=1
        count_var.set(str(counter))

        time.sleep(60/30)


def submit(map_field, entry_field, type):
    print(f' map : { map_field.get()} - task : {entry_field.get()} - {type} ')

    if type == 'goal' or 'station':
        # Travel to any stations(if they connect to the current map)
        nav.travel_to_station(map_field.get(), entry_field.get())

    elif type == 'task':
        # Run a preset task on a map
        nav.connection.run_list_task(map_field.get(), entry_field.get())

    else:
        logging.error(f'Unknown submit action type, {type}')




''' UI '''

# Bind space bar key press event to the function
window.bind("<space>", space_bar_pressed)
# window.bind("<space>", switch_page)

# Initialize the output variable
output = ""

count_var = StringVar()
output_var = StringVar()
count_var.set(str(0))
output_var.set('')

tabControl = ttk.Notebook(window) 
tab1 = ttk.Frame(tabControl, width=390, height=90)

tab2 = ttk.Frame(tabControl, width=390, height=90) 
  
tabControl.add(tab1, text ='    Info    ') 
tabControl.add(tab2, text ='    Task    ') 
tabControl.pack(expand = 1, fill ="both") 


'''
TAB 1
'''

content_label_list = []
# card_stack_frame_p1 = tk.Frame(tab1, bg="white", width=390, height=240, padx=5, pady=5)
# card_stack_frame_p1.pack(padx=5, pady=5)

for i, title in enumerate(titles):

    # Create the title label
    title_label = tk.Label(tab1, text=title, font=("Arial", 12, "bold"), fg=FONT_COLOR, bg='systemTransparent')
    title_label.pack(side=tk.TOP, padx=5, pady=2)


    # Create the content label
    content_label = tk.Label(tab1, textvariable=vars[i], font=("Arial", 26), bg='systemTransparent')
    content_label.pack(side=tk.TOP, padx=5, pady=5)
    content_label_list.append(content_label)

     # Create the title label
    space = tk.Label(tab1, text='', font=("Arial", 12, "bold"), bg='systemTransparent')
    space.pack(side=tk.TOP, padx=5, pady=3)

# # Create a small label in the left upper corner
small_label = tk.Label(window, textvariable=count_var, font=("Arial", 14))
small_label.place(x=5, y=5)

close_button = tk.Button(tab1, text=f"Close", command=lambda: close_window(), width=80, height=30)
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
task_name_entry_field_1.insert(0, f"task_name_1") 
task_name_entry_field_1.pack(side=tk.TOP, padx=5, pady=5)

submit_button_1 = tk.Button(tab2, text=f"Submit 1", command=lambda: submit(map_name_entry_field_1, task_name_entry_field_1, 'station'), width=80)
submit_button_1.pack(side=tk.TOP, padx=5, pady=5)

space = tk.Label(tab2, text='', font=("Arial", 12, "bold"), bg='systemTransparent')
space.pack(side=tk.TOP, padx=5, pady=3)


label_2 = tk.Label(tab2, text="Run task", font=("Arial", 14), bg='systemTransparent')
label_2.pack(side=tk.TOP, padx=5, pady=3)

map_name_entry_field_2 = tk.Entry(tab2, width=80)
map_name_entry_field_2.insert(0, f"Elements05") 
map_name_entry_field_2.pack(side=tk.TOP, padx=5, pady=5)

task_name_entry_field_2 = tk.Entry(tab2, width=80)
task_name_entry_field_2.insert(0, f" task_name_2") 
task_name_entry_field_2.pack(side=tk.TOP, padx=5, pady=5)

submit_button_2 = tk.Button(tab2, text=f"Submit 2", command=lambda: submit(map_name_entry_field_2, task_name_entry_field_2, 'task'), width=80)
submit_button_2.pack(side=tk.TOP, padx=5, pady=5)

space = tk.Label(tab2, text='', font=("Arial", 12, "bold"), bg='systemTransparent')
space.pack(side=tk.TOP, padx=5, pady=3)


''' Message box '''
# Create a frame for the message box
message_box_frame = tk.Frame(tab2, bg="light grey", bd=1, relief=tk.SOLID, width=390, height=50, padx=5, pady=5)
message_box_frame.pack(side=tk.BOTTOM, padx=5, pady=5)


# Create the message label
message_label = tk.Label(message_box_frame, textvariable=output_var, font=("Arial", 14), width=390, height=50)
message_label.pack()

close_button = tk.Button(tab2, text=f"Close", command=lambda: close_window(), width=80, height=30)
close_button.pack(side=tk.BOTTOM, padx=5, pady=5)








# Run the update loop
# if not testing_ui:
update_thread = Thread(target=update_loops)
update_thread.start()
timer_thread = Thread(target=timer)
timer_thread.start()



# Start the GUI event loop
window.mainloop()



    
    
    

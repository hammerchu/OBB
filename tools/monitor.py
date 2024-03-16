import tkinter as tk
from tkinter import *
from tkinter import ttk
from datetime import datetime
import asyncio
import time
from threading import Thread
from bot.classes.connection import Connect
from bot.classes.navigate import Navigate
from bot.tools.utilities import get_scaled_control_map_color

import logging

testing_ui = True

logging.basicConfig(level=logging.INFO)

# Create the main window
window = tk.Tk()
# Set the window title
window.title("OBB Testing")

# Set the window size
window.geometry("400x860")

FONT_COLOR = '#cccccc'

if not testing_ui:
    conn = Connect('192.168.1.102')
    r = conn.login()
    if r:
        auth_token = r
    else:
        output = f'Unable to obtain API token'
        auth_token = ''
    r = conn.get_maps_list()
    print(r)
    # conn.start_nav()
    nav = Navigate()

current_page = 0

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


def submit_button_clicked(index, label_value, entry_value, auth_token):
    eval_str = f'app.{label_value.lower()}({entry_value.lower()})'
    print(f' eval_str : { eval_str} ')

    resp_bot = asyncio.run(eval(eval_str))
    print(f' resp_bot : { resp_bot} ')
    print('--------------------\n')
    # mark_log(resp_bot)

def close_window():
    with open('log', 'a+') as log_file:

        log_file.write(f'\n<section closed at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}>')
        log_file.write('\n')
        # log_file.write(outputs)

    window.destroy()



# Function to change the background color temporarily
def change_background_color():
    # Change the background color to a different color
    window.configure(bg="lightblue")

    # After 0.5 seconds, restore the background color to white
    window.after(500, lambda: window.configure(bg="white"))

    



# Function to handle space bar key press
async def space_bar_pressed(event):
    # Perform your desired actions here
    print("Space bar pressed")
    change_background_color()
    asyncio.run(conn.cmd_vel())

def timer():
    count = 0
    while True:
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
    while True:
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
                position.set(str((r[0], r[1], r[2])))
                orientation.set(str((r[3], r[4], r[5], r[6])))
            # print(f' position : { position.get() } ')
            # print(f' orientation : { orientation.get() } ')
            
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



''' UI '''

# # Run the update loop
# # if not testing_ui:
# update_thread = Thread(target=update_loops)
# update_thread.start()

# Bind space bar key press event to the function
window.bind("<space>", space_bar_pressed)

# Initialize the output variable
output = ""

count_var = StringVar()
output_var = StringVar()
count_var.set(str(0))
output_var.set('')

# Create a frame for the card stack
card_stack_frame = tk.Frame(window, bg="white", width=390, height=90, padx=5, pady=5)
card_stack_frame.pack(padx=5, pady=2)

# Create the content label
content_label = tk.Label(card_stack_frame, text="", font=("Arial", 5))
content_label.pack(side=tk.BOTTOM, padx=5, pady=2)

# Create additional card stacks
content_label_list = []
for i, title in enumerate(titles):
    # Create a frame for the card stack
    card_stack_frame = tk.Frame(window, bg="white", width=390, height=240, padx=5, pady=5)
    card_stack_frame.pack(padx=5, pady=5)

    # Create the title label
    title_label = tk.Label(card_stack_frame, text=title, font=("Arial", 16, "bold"), fg=FONT_COLOR)
    title_label.pack(side=tk.TOP, padx=5, pady=2)


    # Create the content label
    # content_label = tk.Label(card_stack_frame, textvariable=vars[i], font=("Arial", 26))
    content_label = tk.Label(card_stack_frame, textvariable=vars[i], font=("Arial", 26))
    content_label.pack( padx=5, pady=5)
    content_label_list.append(content_label)


    # Create a separator line
    if i < len(titles)-1:
        separator = tk.Frame(card_stack_frame, height=2, width=380, bg="grey")
        separator.pack(side=tk.BOTTOM, pady=2)

# Create a frame for the message box
message_box_frame = tk.Frame(window, bg="light grey", bd=1, relief=tk.SOLID, width=390, height=50, padx=5, pady=5)
message_box_frame.pack(side=tk.BOTTOM, padx=5, pady=5)

# Create the message label
message_label = tk.Label(message_box_frame, textvariable=output_var, font=("Arial", 14), width=390, height=50)
message_label.pack()

# # Create a small label in the left upper corner
small_label = tk.Label(window, textvariable=count_var, font=("Arial", 14))
small_label.place(x=5, y=5)

# Create a close button at the lower right corner of the entire GUI
close_button = tk.Button(message_box_frame, text="Close", command=close_window, height= 3, width=10)

# Run the update loop
# if not testing_ui:
update_thread = Thread(target=update_loops)
update_thread.start()
timer_thread = Thread(target=timer)
timer_thread.start()

# Start the GUI event loop
window.mainloop()



    
    
    

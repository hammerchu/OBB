import zone_cmd
from bot.classes import call
from bot.tools import joystick


if __name__ == '__main__':
    print('running sandbox')

    c = call.Call('m', 30, False)
    print(c.video_quality)
    eval('zone_cmd.supervise')(c)
    print(c.video_quality)
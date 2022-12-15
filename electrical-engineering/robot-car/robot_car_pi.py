# pip install gpiozero pygame
import os
import gpiozero
import pygame
from pygame.constants import *

# 通过 gpio 连接电机
motor_l_head = gpiozero.Motor(6,13)
motor_l_tail = gpiozero.Motor(19,26)

motor_r_tail = gpiozero.Motor(18, 17)
motor_r_head = gpiozero.Motor(27,22)

# 初始化 pygame 用来读取 xbox one 蓝牙手柄的信号

# http://www.pygame.org/wiki/HeadlessNoWindowsNeeded
# set SDL to use the dummy NULL video driver,
#   so it doesn't need a windowing system.
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
if pygame.joystick.get_count() == 0:
    print(f"未连接任何手柄控制器，请先连接！")
    exit(0)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"已连接手柄控制器：{joystick.get_name()}")


def run(x_value, y_value):
    y_abs_value = min(abs(y_value), 1)

    x_action = "turn_right" if x_value >= 0 else "turn_left"
    x_abs_value = min(abs(x_value), 1)

    if x_action == "turn_right":
        l_speed = min(1.0, y_value + x_abs_value)
        r_speed = max(-1.0, y_value - x_abs_value)
    else:
        l_speed = max(-1.0, y_value - x_abs_value)
        r_speed = min(1.0, y_value + x_abs_value)


    l_motor_action = "forward" if l_speed >= 0 else "backward"
    r_motor_action = "forward" if r_speed >= 0 else "backward"

    l_speed = abs(l_speed)
    r_speed = abs(r_speed)

    print(f"左轮速度：{l_speed:.2} 方向：{l_motor_action}；右轮速度：{r_speed:.2}，方向 {r_motor_action}")

    motor_l_tail.__getattribute__(l_motor_action)(l_speed)
    motor_l_head.__getattribute__(l_motor_action)(l_speed)
    motor_r_head.__getattribute__(r_motor_action)(r_speed)
    motor_r_tail.__getattribute__(r_motor_action)(r_speed)


def main():
    x_value = 0
    y_value = 0

    while True or KeyboardInterrupt:
        for e in pygame.event.get():
            # <Event(1536-JoyAxisMotion {'joy': 0, 'instance_id': 0, 'axis': 1, 'value': 0.8169499801629688})>
            # 左摇杆（平面直角坐标系）
            #   axis=0 左右
            #   axis=1 上下
            # 右摇杆：2 3
            if e.type == JOYAXISMOTION:
                if  e.axis == 0:
                    x_value = e.value
                elif e.axis == 1:
                    y_value = e.value

                run(x_value, y_value)
            # <Event(1539-JoyButtonDown {'joy': 0, 'instance_id': 0, 'button': 4})>
            if e.type == JOYBUTTONDOWN:
                print("JOYBUTTONDOWN", e.button)


main()
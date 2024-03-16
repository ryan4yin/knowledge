# 使用 Xbox 蓝牙手柄遥控机械手
# pip3 install pigpio gpiozero pygame
# 同时还需要提前手动安装 pigpiod 并启动后台运行
import os
import time
import gpiozero
import pygame
from pygame.constants import *

from gpiozero.pins.pigpio import PiGPIOFactory

factory = PiGPIOFactory()

# 通过 gpio 连接舵机
base_servo = gpiozero.Servo(13, pin_factory=factory)
left_servo = gpiozero.Servo(14, pin_factory=factory)
right_servo = gpiozero.Servo(4, pin_factory=factory)
# 钳子舵机，不过这个舵机被我整坏了...
# claw_servo = gpiozero.Servo(x, pin_factory=factory)

max_speed = 0.03

# # 初始化 pygame 用来读取 xbox one 蓝牙手柄的信号

# # http://www.pygame.org/wiki/HeadlessNoWindowsNeeded
# # set SDL to use the dummy NULL video driver,
# #   so it doesn't need a windowing system.
os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
if pygame.joystick.get_count() == 0:
    print(f"未连接任何手柄控制器，请先连接！")
    exit(0)

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"已连接手柄控制器：{joystick.get_name()}")

def calculate(speed, current_position):
    distance = speed * max_speed
    new_position = current_position + distance

    if new_position < -1:
        print("new", -1)
        return -1
    if new_position > 1:
        print("new", 1)

        return 1

    return new_position

left_servo.max()

def main():
    left_value = 0
    right_value = 0
    base_value = 0

    while True or KeyboardInterrupt:
        e =  pygame.event.poll()
        # <Event(1536-JoyAxisMotion {'joy': 0, 'instance_id': 0, 'axis': 1, 'value': 0.8169499801629688})>
        if e.type == JOYAXISMOTION:
            # 左摇杆（平面直角坐标系）
            if  e.axis == 0: # x 轴，左舵机
                left_value = e.value
            elif e.axis == 1:  # y 轴，右舵机
                right_value = e.value
            # 右摇杆
            elif  e.axis == 2:  # x 轴，基座旋转
                base_value = e.value
            # elif e.axis == 3:  # Y 轴，钳子收缩
            #     claw_value = e.value

        # <Event(1539-JoyButtonDown {'joy': 0, 'instance_id': 0, 'button': 4})>
        if e.type == JOYBUTTONDOWN:
            print("JOYBUTTONDOWN", e.button)

        left_servo.value = calculate(left_value, left_servo.value)
        right_servo.value = calculate(right_value, right_servo.value)
        base_servo.value = calculate(base_value, base_servo.value)
        time.sleep(0.001)
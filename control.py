# -*- coding: utf-8 -*-
#机械臂控制(使用的是开塔机器人的机械臂)
import wlkatapython
import serial
import time
import cv2
import numpy as np

class Control:
    def control_robot_fang(self, arg1, arg2):
        def execute_robot_arm_control():
            print("gei positions")
            # 定义机器人的坐标位置列表
            coordinate_g = [
                [arg1[0], arg1[1], 40.72, 0, 0, 0],  # 初始位置
                [arg1[0], arg1[1], 30.72, 0, 0, 0],  # 抓取位置
                [arg1[0], arg1[1], 40.72, 0, 0, 0],  # 提升（写死）
                [arg2[0], arg2[1], 40.72, 0, 0, 0],  # 移动到放置位置
                [arg2[0], arg2[1], 30.72, 0, 0, 0],  # 放置位置
                [arg2[0], arg2[1], 40.72, 0, 0, 0],  # 提升（写死）
            ]
            # 设置串口和波特率
            serial1 = serial.Serial("/dev/ttyUSB0", 115200)
            print("set serial")

            # 创建 mirobot1 对象
            mirobot1 = wlkatapython.Wlkata_UART()
            mirobot1.init(serial1, -1)  # 设置机器人原点
            print("creat mirobot1")

            # 如果机器人处于 Alarm 状态则进行复位
            if mirobot1.getState() == "Alarm":
                mirobot1.homing()

            # 遍历坐标位置，控制机械臂运动和气泵
            for i in range(6):
                while mirobot1.getState() != "Idle":
                    print("robot 1:", mirobot1.getState())

                # 移动到指定的坐标位置
                mirobot1.writecoordinate(
                    0, 0, 
                    coordinate_g[i][0], coordinate_g[i][1], coordinate_g[i][2],
                    coordinate_g[i][3], coordinate_g[i][4], coordinate_g[i][5]
                )

                # 控制气泵的吸气和放气
                if i == 1:  # 抵达抓取位置
                    mirobot1.pump(1)  # 气泵放气
                    time.sleep(1)
                elif i == 4:  # 抵达放置位置
                    mirobot1.pump(2)  # 气泵吸气
                    time.sleep(1)  # 等待 1 秒

            # 关闭气泵并将机器人回到初始位置
            mirobot1.pump(0)
            mirobot1.zero()

        return execute_robot_arm_control
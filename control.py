# -*- coding: utf-8 -*-
#��е�ۿ���(ʹ�õ��ǿ��������˵Ļ�е��)
import wlkatapython
import serial
import time
import cv2
import numpy as np

class Control:
    def control_robot_fang(self, arg1, arg2):
        def execute_robot_arm_control():
            print("gei positions")
            # ��������˵�����λ���б�
            coordinate_g = [
                [arg1[0], arg1[1], 40.72, 0, 0, 0],  # ��ʼλ��
                [arg1[0], arg1[1], 30.72, 0, 0, 0],  # ץȡλ��
                [arg1[0], arg1[1], 40.72, 0, 0, 0],  # ������д����
                [arg2[0], arg2[1], 40.72, 0, 0, 0],  # �ƶ�������λ��
                [arg2[0], arg2[1], 30.72, 0, 0, 0],  # ����λ��
                [arg2[0], arg2[1], 40.72, 0, 0, 0],  # ������д����
            ]
            # ���ô��ںͲ�����
            serial1 = serial.Serial("/dev/ttyUSB0", 115200)
            print("set serial")

            # ���� mirobot1 ����
            mirobot1 = wlkatapython.Wlkata_UART()
            mirobot1.init(serial1, -1)  # ���û�����ԭ��
            print("creat mirobot1")

            # ��������˴��� Alarm ״̬����и�λ
            if mirobot1.getState() == "Alarm":
                mirobot1.homing()

            # ��������λ�ã����ƻ�е���˶�������
            for i in range(6):
                while mirobot1.getState() != "Idle":
                    print("robot 1:", mirobot1.getState())

                # �ƶ���ָ��������λ��
                mirobot1.writecoordinate(
                    0, 0, 
                    coordinate_g[i][0], coordinate_g[i][1], coordinate_g[i][2],
                    coordinate_g[i][3], coordinate_g[i][4], coordinate_g[i][5]
                )

                # �������õ������ͷ���
                if i == 1:  # �ִ�ץȡλ��
                    mirobot1.pump(1)  # ���÷���
                    time.sleep(1)
                elif i == 4:  # �ִ����λ��
                    mirobot1.pump(2)  # ��������
                    time.sleep(1)  # �ȴ� 1 ��

            # �ر����ò��������˻ص���ʼλ��
            mirobot1.pump(0)
            mirobot1.zero()

        return execute_robot_arm_control
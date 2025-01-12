#coding=utf-8
#���۱궨 ����ת���������Ϊ��е������
import numpy as np
import cv2

# �µ�Բ���������
STC_points_camera = np.array([
    [211, 102],
    [267, 130],
    [323, 159],
    [178, 155],
    [234, 184],
    [290, 212],
    [145, 209],
    [201, 238],
    [257, 266],

])

# �µ�Բ�Ļ�е������
STC_points_robot = np.array([
    (12, 164.6),  # ��һ����
    (12, 190.6),  # �ڶ�����
    (12, 225.6),  # ��������
    (-18, 165.6),  # ���ĸ���
    (-18, 195.6),  # �������
    (-18, 225.6),  # ��������
    (-53, 165.6),  # ���߸���
    (-53, 190.6),  # �ڰ˸���
    (-53, 225.6)   # �ھŸ���
])

# ���۱궨����
class HandInEyeCalibration:

    def get_m(self, points_camera, points_robot):
        # """
        # ȡ���������ת������������ķ������
        # :param points_camera:
        # :param points_robot:
        # :return:
        # """
        # ȷ�������㼯����������Ҫ�����󣬷�������None
        m, _ = cv2.estimateAffine2D(points_camera, points_robot)
        return m

    def get_points_robot(self, x_camera, y_camera):
        # """
        # �������ͨ���������任ȡ�û�������
        # :param x_camera:
        # :param y_camera:
        # :return:
        # """
        m = self.get_m(STC_points_camera, STC_points_robot)
        robot_y = (m[0][0] * x_camera) + (m[0][1] * y_camera) + m[0][2]
        robot_x = (m[1][0] * x_camera) + (m[1][1] * y_camera) + m[1][2]
        return robot_x, robot_y

# ʹ��ʾ��
calibration = HandInEyeCalibration()
camera_x, camera_y = 255, 93
robot_x, robot_y = calibration.get_points_robot(camera_x, camera_y)
print(f"Robot coordinates: x = {robot_x}, y = {robot_y}")

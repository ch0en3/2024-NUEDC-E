#coding=utf-8
#手眼标定 用于转换相机坐标为机械臂坐标
import numpy as np
import cv2

# 新的圆心相机坐标
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

# 新的圆心机械臂坐标
STC_points_robot = np.array([
    (12, 164.6),  # 第一格子
    (12, 190.6),  # 第二格子
    (12, 225.6),  # 第三格子
    (-18, 165.6),  # 第四格子
    (-18, 195.6),  # 第五格子
    (-18, 225.6),  # 第六格子
    (-53, 165.6),  # 第七格子
    (-53, 190.6),  # 第八格子
    (-53, 225.6)   # 第九格子
])

# 手眼标定方法
class HandInEyeCalibration:

    def get_m(self, points_camera, points_robot):
        # """
        # 取得相机坐标转换到机器坐标的仿射矩阵
        # :param points_camera:
        # :param points_robot:
        # :return:
        # """
        # 确保两个点集的数量级不要差距过大，否则会输出None
        m, _ = cv2.estimateAffine2D(points_camera, points_robot)
        return m

    def get_points_robot(self, x_camera, y_camera):
        # """
        # 相机坐标通过仿射矩阵变换取得机器坐标
        # :param x_camera:
        # :param y_camera:
        # :return:
        # """
        m = self.get_m(STC_points_camera, STC_points_robot)
        robot_y = (m[0][0] * x_camera) + (m[0][1] * y_camera) + m[0][2]
        robot_x = (m[1][0] * x_camera) + (m[1][1] * y_camera) + m[1][2]
        return robot_x, robot_y

# 使用示例
calibration = HandInEyeCalibration()
camera_x, camera_y = 255, 93
robot_x, robot_y = calibration.get_points_robot(camera_x, camera_y)
print(f"Robot coordinates: x = {robot_x}, y = {robot_y}")

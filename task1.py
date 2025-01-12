#coding=utf-8
#一个用于演示如何调用视觉数据并转换为机械臂坐标并加上机械臂控制
#任务1 用于抓取一个黑棋子并且放置在棋盘第五个格子的位置
import cv2
from visual import vision
from transform import HandInEyeCalibration
from control import Control

visual = vision()
handle = HandInEyeCalibration()
control = Control()

def main():
    cap = cv2.VideoCapture(0)  # 打开摄像头
    
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Frame capture failed.")
            break
        
        edges = visual.process_img(frame)  # 处理图像，进行边缘检测
        rect = visual.get_chessboard_coordinates(edges)  # 获取棋盘四个角的坐标
        frame_with_corners = visual.draw_chessboard_corners(frame, rect)  # 绘制棋盘的四个角
        marked_frame, positions = visual.draw_grid_numbers_and_get_positions(frame_with_corners, rect)  # 绘制网格数字并获取每个格子的中心坐标
        
        marked_frame, piece_coordinates, black_piece_positions, white_piece_positions = visual.detect_and_mark_pieces(marked_frame, positions)  # 检测和标记棋子
        
        # 确保检测到了黑白棋子
        if not white_piece_positions or not black_piece_positions:
            print("Error: Could not detect both black and white pieces.")
            cap.release()
            return None
        

        #获取黑白棋子坐标
        one_white = white_piece_positions[1]
        one_black = black_piece_positions[1]

        #获取棋盘坐标
        one = positions[0]
        five = positions[4]

        #转换为机械臂坐标
        five_robot_coords = handle.get_points_robot(five[0], five[1])
        one_robot_coords = handle.get_points_robot(one[0], one[1])
        one_white_coords = handle.get_points_robot(one_white[0],one_white[1])
        one_black_coords = handle.get_points_robot(one_black[0],one_black[1])

        #打印坐标
        print(f'zuobiao:{five_robot_coords}')
        print(f'zuobiao:{one_robot_coords}')
        print(f'qizi_zuobiao:{one_white_coords}')
        print(f'qizi_zuobiao:{one_black_coords}')
        
        control_arm = control.control_robot_fang(one_white_coords,five_robot_coords)
        control_arm()

        break

    cv2.imshow('Marked Grid', marked_frame)  # 显示标记棋子和网格的图像
    cap.release()
    cv2.destroyAllWindows()  # 释放资源并关闭所有窗口

if __name__ == "__main__":
    main()

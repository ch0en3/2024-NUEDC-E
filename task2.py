#coding=utf-8
import cv2
import sys
import time
from visual import vision
from transform import HandInEyeCalibration
from control import Control

visual = vision()
handle = HandInEyeCalibration()
control = Control()

def main():
    if len(sys.argv) != 5:
        print("Usage: python script.py <grid_number1> <grid_number2> <grid_number3> <grid_number4>")
        return

    try:
        grid_numbers = [int(arg) for arg in sys.argv[1:]]
        if any(not 1 <= num <= 9 for num in grid_numbers):
            raise ValueError
    except ValueError:
        print("Error: Please enter grid numbers between 1 and 9.")
        return

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
        if len(white_piece_positions) < 2 or len(black_piece_positions) < 2:
            print("Error: Could not detect at least two black and two white pieces.")
            continue

        # 打开一个新窗口显示标记的图像
        cv2.imshow('Marked Grid', marked_frame)
        cv2.waitKey(1000)  # 等待一秒以显示图像

        cap.release()
        cv2.destroyAllWindows()  # 释放资源并关闭所有窗口

        # 预定义放置的位置
        place_positions = [positions[num - 1] for num in grid_numbers]

        # 白棋子坐标
        white_piece_coords_list = [white_piece_positions[0], white_piece_positions[1]]
        for i in range(2):
            white_piece_coords = handle.get_points_robot(white_piece_coords_list[i][0], white_piece_coords_list[i][1])
            place_coords = handle.get_points_robot(place_positions[i][0], place_positions[i][1])
            control_arm = control.control_robot_fang(white_piece_coords, place_coords)
            control_arm()
            print(f"Placed white piece at grid {grid_numbers[i]}")
            
            # 等待机械臂完成操作并返回原位
            time.sleep(3)  # 根据机械臂操作时间进行适当调整

        # 黑棋子坐标
        black_piece_coords_list = [black_piece_positions[0], black_piece_positions[1]]
        for i in range(2):
            black_piece_coords = handle.get_points_robot(black_piece_coords_list[i][0], black_piece_coords_list[i][1])
            place_coords = handle.get_points_robot(place_positions[i+2][0], place_positions[i+2][1])
            control_arm = control.control_robot_fang(black_piece_coords, place_coords)
            control_arm()
            print(f"Placed black piece at grid {grid_numbers[i+2]}")

            # 等待机械臂完成操作并返回原位
            time.sleep(3)  # 根据机械臂操作时间进行适当调整

        break  # 任务完成，退出循环

if __name__ == "__main__":
    main()

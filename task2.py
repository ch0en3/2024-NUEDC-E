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

    cap = cv2.VideoCapture(0)  # ������ͷ
    
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Frame capture failed.")
            break
        
        edges = visual.process_img(frame)  # ����ͼ�񣬽��б�Ե���
        rect = visual.get_chessboard_coordinates(edges)  # ��ȡ�����ĸ��ǵ�����
        frame_with_corners = visual.draw_chessboard_corners(frame, rect)  # �������̵��ĸ���
        marked_frame, positions = visual.draw_grid_numbers_and_get_positions(frame_with_corners, rect)  # �����������ֲ���ȡÿ�����ӵ���������
        
        marked_frame, piece_coordinates, black_piece_positions, white_piece_positions = visual.detect_and_mark_pieces(marked_frame, positions)  # ���ͱ������
        
        # ȷ����⵽�˺ڰ�����
        if len(white_piece_positions) < 2 or len(black_piece_positions) < 2:
            print("Error: Could not detect at least two black and two white pieces.")
            continue

        # ��һ���´�����ʾ��ǵ�ͼ��
        cv2.imshow('Marked Grid', marked_frame)
        cv2.waitKey(1000)  # �ȴ�һ������ʾͼ��

        cap.release()
        cv2.destroyAllWindows()  # �ͷ���Դ���ر����д���

        # Ԥ������õ�λ��
        place_positions = [positions[num - 1] for num in grid_numbers]

        # ����������
        white_piece_coords_list = [white_piece_positions[0], white_piece_positions[1]]
        for i in range(2):
            white_piece_coords = handle.get_points_robot(white_piece_coords_list[i][0], white_piece_coords_list[i][1])
            place_coords = handle.get_points_robot(place_positions[i][0], place_positions[i][1])
            control_arm = control.control_robot_fang(white_piece_coords, place_coords)
            control_arm()
            print(f"Placed white piece at grid {grid_numbers[i]}")
            
            # �ȴ���е����ɲ���������ԭλ
            time.sleep(3)  # ���ݻ�е�۲���ʱ������ʵ�����

        # ����������
        black_piece_coords_list = [black_piece_positions[0], black_piece_positions[1]]
        for i in range(2):
            black_piece_coords = handle.get_points_robot(black_piece_coords_list[i][0], black_piece_coords_list[i][1])
            place_coords = handle.get_points_robot(place_positions[i+2][0], place_positions[i+2][1])
            control_arm = control.control_robot_fang(black_piece_coords, place_coords)
            control_arm()
            print(f"Placed black piece at grid {grid_numbers[i+2]}")

            # �ȴ���е����ɲ���������ԭλ
            time.sleep(3)  # ���ݻ�е�۲���ʱ������ʵ�����

        break  # ������ɣ��˳�ѭ��

if __name__ == "__main__":
    main()

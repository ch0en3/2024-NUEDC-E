#coding=utf-8
#һ��������ʾ��ε����Ӿ����ݲ�ת��Ϊ��е�����겢���ϻ�е�ۿ���
#����1 ����ץȡһ�������Ӳ��ҷ��������̵�������ӵ�λ��
import cv2
from visual import vision
from transform import HandInEyeCalibration
from control import Control

visual = vision()
handle = HandInEyeCalibration()
control = Control()

def main():
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
        if not white_piece_positions or not black_piece_positions:
            print("Error: Could not detect both black and white pieces.")
            cap.release()
            return None
        

        #��ȡ�ڰ���������
        one_white = white_piece_positions[1]
        one_black = black_piece_positions[1]

        #��ȡ��������
        one = positions[0]
        five = positions[4]

        #ת��Ϊ��е������
        five_robot_coords = handle.get_points_robot(five[0], five[1])
        one_robot_coords = handle.get_points_robot(one[0], one[1])
        one_white_coords = handle.get_points_robot(one_white[0],one_white[1])
        one_black_coords = handle.get_points_robot(one_black[0],one_black[1])

        #��ӡ����
        print(f'zuobiao:{five_robot_coords}')
        print(f'zuobiao:{one_robot_coords}')
        print(f'qizi_zuobiao:{one_white_coords}')
        print(f'qizi_zuobiao:{one_black_coords}')
        
        control_arm = control.control_robot_fang(one_white_coords,five_robot_coords)
        control_arm()

        break

    cv2.imshow('Marked Grid', marked_frame)  # ��ʾ������Ӻ������ͼ��
    cap.release()
    cv2.destroyAllWindows()  # �ͷ���Դ���ر����д���

if __name__ == "__main__":
    main()

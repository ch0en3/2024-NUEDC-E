#coding=utf-8
#�����汾 Ŀǰ�ܹ�׼ȷʶ�����������̺����� ���ҽ�����洢����
#�Ӿ�����

import cv2
import numpy as np


class vision():
# ����ͼ���Խ��б�Ե���
    def process_img(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # תΪ�Ҷ�ͼ
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # ��˹ģ��
        edges = cv2.Canny(blurred, 50, 150)  # Canny��Ե���
        return edges

    # ��ȡ���̵��ĸ��ǵ�����
    def get_chessboard_coordinates(self,edges):
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        square, area = None, 0
        
        for item in contours:
            hull = cv2.convexHull(item)  # ��ȡ͹��
            epsilon = 0.1 * cv2.arcLength(hull, True)  # ������ƶ���ε��ܳ�
            approx = cv2.approxPolyDP(hull, epsilon, True)  # ���ƶ����
            
            if len(approx) == 4 and cv2.isContourConvex(approx):  # ����Ƿ�Ϊ͹�ı���
                ps = np.reshape(approx, (4, 2))  # ��������Ϊ4x2����
                ps = ps[np.lexsort((ps[:, 0],))]  # ��x��������
                lt, lb = ps[:2][np.lexsort((ps[:2, 1],))]  # ���ϡ�����
                rt, rb = ps[2:][np.lexsort((ps[2:, 1],))]  # ���ϡ�����
                a = cv2.contourArea(approx)  # �������
                
                # �����߱�
                width = np.linalg.norm(rt - lt)
                height = np.linalg.norm(lb - lt)
                aspect_ratio = width / height
                
                if 0.9 < aspect_ratio < 1.1 and a > area:  # ����߱��Ƿ�ӽ�1
                    area = a
                    square = (lt, lb, rt, rb)  # ������������������
        
        if square is None:
            print('cannot get')
        # else:
        #     print('coordinate')
        #     print((square[0][0], square[0][1]))
        #     print((square[1][0], square[1][1]))
        #     print((square[2][0], square[2][1]))
        #     print((square[3][0], square[3][1]))
        
        return square



    # ��ͼ���ϻ������̵��ĸ���
    def draw_chessboard_corners(self, frame, rect):
        if rect is not None:
            for point in rect:
                cv2.drawMarker(frame, tuple(point), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
        return frame

    # �����������ֲ���ȡÿ�����ӵ��������꣬��������������洢���б���

    def draw_grid_numbers_and_get_positions(self, frame, rect):
        positions = [[0, 0] for _ in range(9)]  # ��ʼ����СΪ9���б�    
        if rect is None:
            return frame, positions,0,0
        
        lt, lb, rt, rb = rect  # �ĸ��ǵ�
        width = int(np.linalg.norm(rt - lt))  # ������
        height = int(np.linalg.norm(lb - lt))  # ����߶�
        
        x_base = (rt - lt) / np.linalg.norm(rt - lt)
        y_base = (lb - lt) / np.linalg.norm(lb - lt)

        cell_width = width // 3  # ÿ�����ӵĿ��
        cell_height = height // 3  # ÿ�����ӵĸ߶�

        transform_matrix = np.array([x_base, y_base]).T
        #print(f"Transform matrix:\n{transform_matrix}")
        
        for i in range(3):
            for j in range(3):
                x1 = j * cell_width
                y1 = i * cell_height
                text = np.array([x1 + cell_width // 3, y1 + 2 * cell_height // 3])
                transformed_text = np.dot(transform_matrix, text) + lt
                cv2.putText(frame, str(i * 3 + j + 1), (int(transformed_text[0]), int(transformed_text[1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                center = np.array([x1 + cell_width // 2, y1 + cell_height // 2])
                #print(f"Transformed text: {transformed_text}")
                transformed_center = np.dot(transform_matrix, center) + lt
                #print(f"Transformed center: {transformed_center}")  # ��ӡ�任���center
                positions[i * 3 + j] = [int(transformed_center[0]), int(transformed_center[1])]  # �洢ÿ�����ӵ���������
        
        return frame,positions
    
    def adjust_brightness(self,image, value):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.subtract(v, value)
        v = cv2.max(v, 0)
        final_hsv = cv2.merge((h, s, v))
        image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return image


    # ���ͱ������
    def detect_and_mark_pieces(self, frame, positions):
        frame = self.adjust_brightness(frame, 35)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # תΪ�Ҷ�ͼ
        # ��˹ģ��
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=30)  # ����Բ���
        
        piece_coordinates = {'black': [], 'white': []}
        black_piece_positions = []  # �洢�����ӵ�����
        white_piece_positions = []  # �洢�����ӵ�����
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")  # �������벢ת��Ϊ����
            im_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)  # תΪHSV��ɫ�ռ�
            
            for (x, y, r) in circles:
                # �ҵ�����ĸ�������
                distances = [np.sqrt((px - x)**2 + (py - y)**2) for (px, py) in positions]
                closest_pos = positions[np.argmin(distances)]
                
                # ��ȡ����Ȥ����
                roi = im_hsv[y-5:y+5, x-5:x+5]
                if roi.size == 0:  # �������Ȥ����Ϊ�գ�����
                    continue
                mean_s = np.mean(roi[:, :, 1])  # ���㱥�ͶȾ�ֵ
                mean_v = np.mean(roi[:, :, 2])  # �������Ⱦ�ֵ
                
                if 0 < mean_v < 110:  # ������
                    piece_coordinates['black'].append(closest_pos)
                    black_piece_positions.append((x, y))  # ��¼�����ӵ�����
                    cv2.circle(frame, (x, y), r, (0, 0, 0), 2)
                    cv2.putText(frame, 'B', (x-10, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
                    print(f"White piece detected at: {(x, y)}")  # ��ӡ����������

                elif 110 < mean_v < 256:  # ������
                    piece_coordinates['white'].append(closest_pos)
                    white_piece_positions.append((x, y))  # ��¼�����ӵ�����
                    cv2.circle(frame, (x, y), r, (255, 255, 255), 2)
                    cv2.putText(frame, 'W', (x-10, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                    print(f"White piece detected at: {(x, y)}")  # ��ӡ����������

        return frame, piece_coordinates, black_piece_positions, white_piece_positions

# def main():
#     cap = cv2.VideoCapture(0)  # ������ͷ
#     if not cap.isOpened():
#         print("Error: Could not open video source.")
#         return
    
#     while True:
#         ret, frame = cap.read()
#         if not ret or frame is None:
#             print("Error: Frame capture failed.")
#             break
        
#         edges = process_img(frame)  # ����ͼ�񣬽��б�Ե���
#         rect = get_chessboard_coordinates(edges)  # ��ȡ�����ĸ��ǵ�����
#         frame_with_corners = draw_chessboard_corners(frame, rect)  # �������̵��ĸ���
#         marked_frame, positions = draw_grid_numbers_and_get_positions(frame_with_corners, rect)  # �����������ֲ���ȡÿ�����ӵ���������
        
#         marked_frame, piece_coordinates, black_piece_positions, white_piece_positions = detect_and_mark_pieces(marked_frame, positions)  # ���ͱ������
        
#         cv2.imshow('Marked Grid', marked_frame)  # ��ʾ������Ӻ������ͼ��
        
#         if cv2.waitKey(1) & 0xFF == ord('q'):  # ����q���˳�
#             break
    
#     cap.release()
#     cv2.destroyAllWindows()  # �ͷ���Դ���ر����д���

# if __name__ == "__main__":
#     main()

#coding=utf-8
#基础版本 目前能够准确识别正方形棋盘和棋子 并且将坐标存储起来
#视觉处理

import cv2
import numpy as np


class vision():
# 处理图像以进行边缘检测
    def process_img(self,frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # 高斯模糊
        edges = cv2.Canny(blurred, 50, 150)  # Canny边缘检测
        return edges

    # 获取棋盘的四个角的坐标
    def get_chessboard_coordinates(self,edges):
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        square, area = None, 0
        
        for item in contours:
            hull = cv2.convexHull(item)  # 获取凸包
            epsilon = 0.1 * cv2.arcLength(hull, True)  # 计算近似多边形的周长
            approx = cv2.approxPolyDP(hull, epsilon, True)  # 近似多边形
            
            if len(approx) == 4 and cv2.isContourConvex(approx):  # 检查是否为凸四边形
                ps = np.reshape(approx, (4, 2))  # 重新塑形为4x2矩阵
                ps = ps[np.lexsort((ps[:, 0],))]  # 按x坐标排序
                lt, lb = ps[:2][np.lexsort((ps[:2, 1],))]  # 左上、左下
                rt, rb = ps[2:][np.lexsort((ps[2:, 1],))]  # 右上、右下
                a = cv2.contourArea(approx)  # 计算面积
                
                # 计算宽高比
                width = np.linalg.norm(rt - lt)
                height = np.linalg.norm(lb - lt)
                aspect_ratio = width / height
                
                if 0.9 < aspect_ratio < 1.1 and a > area:  # 检查宽高比是否接近1
                    area = a
                    square = (lt, lb, rt, rb)  # 更新最大面积的正方形
        
        if square is None:
            print('cannot get')
        # else:
        #     print('coordinate')
        #     print((square[0][0], square[0][1]))
        #     print((square[1][0], square[1][1]))
        #     print((square[2][0], square[2][1]))
        #     print((square[3][0], square[3][1]))
        
        return square



    # 在图像上绘制棋盘的四个角
    def draw_chessboard_corners(self, frame, rect):
        if rect is not None:
            for point in rect:
                cv2.drawMarker(frame, tuple(point), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
        return frame

    # 绘制网格数字并获取每个格子的中心坐标，将格子中心坐标存储在列表当中

    def draw_grid_numbers_and_get_positions(self, frame, rect):
        positions = [[0, 0] for _ in range(9)]  # 初始化大小为9的列表    
        if rect is None:
            return frame, positions,0,0
        
        lt, lb, rt, rb = rect  # 四个角点
        width = int(np.linalg.norm(rt - lt))  # 计算宽度
        height = int(np.linalg.norm(lb - lt))  # 计算高度
        
        x_base = (rt - lt) / np.linalg.norm(rt - lt)
        y_base = (lb - lt) / np.linalg.norm(lb - lt)

        cell_width = width // 3  # 每个格子的宽度
        cell_height = height // 3  # 每个格子的高度

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
                #print(f"Transformed center: {transformed_center}")  # 打印变换后的center
                positions[i * 3 + j] = [int(transformed_center[0]), int(transformed_center[1])]  # 存储每个格子的中心坐标
        
        return frame,positions
    
    def adjust_brightness(self,image, value):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.subtract(v, value)
        v = cv2.max(v, 0)
        final_hsv = cv2.merge((h, s, v))
        image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return image


    # 检测和标记棋子
    def detect_and_mark_pieces(self, frame, positions):
        frame = self.adjust_brightness(frame, 35)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转为灰度图
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=30)  # 霍夫圆检测
        
        piece_coordinates = {'black': [], 'white': []}
        black_piece_positions = []  # 存储黑棋子的坐标
        white_piece_positions = []  # 存储白棋子的坐标
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")  # 四舍五入并转换为整数
            im_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)  # 转为HSV颜色空间
            
            for (x, y, r) in circles:
                # 找到最近的格子中心
                distances = [np.sqrt((px - x)**2 + (py - y)**2) for (px, py) in positions]
                closest_pos = positions[np.argmin(distances)]
                
                # 提取感兴趣区域
                roi = im_hsv[y-5:y+5, x-5:x+5]
                if roi.size == 0:  # 如果感兴趣区域为空，跳过
                    continue
                mean_s = np.mean(roi[:, :, 1])  # 计算饱和度均值
                mean_v = np.mean(roi[:, :, 2])  # 计算亮度均值
                
                if 0 < mean_v < 110:  # 检测黑棋
                    piece_coordinates['black'].append(closest_pos)
                    black_piece_positions.append((x, y))  # 记录黑棋子的坐标
                    cv2.circle(frame, (x, y), r, (0, 0, 0), 2)
                    cv2.putText(frame, 'B', (x-10, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
                    print(f"White piece detected at: {(x, y)}")  # 打印白棋子坐标

                elif 110 < mean_v < 256:  # 检测白棋
                    piece_coordinates['white'].append(closest_pos)
                    white_piece_positions.append((x, y))  # 记录白棋子的坐标
                    cv2.circle(frame, (x, y), r, (255, 255, 255), 2)
                    cv2.putText(frame, 'W', (x-10, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                    print(f"White piece detected at: {(x, y)}")  # 打印白棋子坐标

        return frame, piece_coordinates, black_piece_positions, white_piece_positions

# def main():
#     cap = cv2.VideoCapture(0)  # 打开摄像头
#     if not cap.isOpened():
#         print("Error: Could not open video source.")
#         return
    
#     while True:
#         ret, frame = cap.read()
#         if not ret or frame is None:
#             print("Error: Frame capture failed.")
#             break
        
#         edges = process_img(frame)  # 处理图像，进行边缘检测
#         rect = get_chessboard_coordinates(edges)  # 获取棋盘四个角的坐标
#         frame_with_corners = draw_chessboard_corners(frame, rect)  # 绘制棋盘的四个角
#         marked_frame, positions = draw_grid_numbers_and_get_positions(frame_with_corners, rect)  # 绘制网格数字并获取每个格子的中心坐标
        
#         marked_frame, piece_coordinates, black_piece_positions, white_piece_positions = detect_and_mark_pieces(marked_frame, positions)  # 检测和标记棋子
        
#         cv2.imshow('Marked Grid', marked_frame)  # 显示标记棋子和网格的图像
        
#         if cv2.waitKey(1) & 0xFF == ord('q'):  # 按下q键退出
#             break
    
#     cap.release()
#     cv2.destroyAllWindows()  # 释放资源并关闭所有窗口

# if __name__ == "__main__":
#     main()

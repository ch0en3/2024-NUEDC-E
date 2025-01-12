#coding=utf-8
#赢棋算法

import cv2
import numpy as np
from visual import vision
from transform import HandInEyeCalibration
from control import Control

class tictactoe:
    def __init__(self):
        self.board = np.zeros((3, 3), dtype=int)  # 初始化棋盘矩阵为全0
        self.player_color = 'black'
        self.machine_color = 'white'
        # self.board_width = board_width
        # self.board_height = board_height
    
    # param positions -- 棋盘格中心点坐标矩阵
    def update_board(self, piece_coordinates, positions): ##更新棋盘
        self.board.fill(0)  # 清空棋盘
        for color, positions in piece_coordinates.items():
            for pos in positions:
                i, j = self.get_grid_position(pos, positions)
                if 0 <= i < 3 and 0 <= j < 3:  # 边界检查
                    if color == self.player_color:
                        self.board[i, j] = 1  # 人类标志位为1
                    elif color == self.machine_color:
                        self.board[i, j] = -1  # 机器标志位为-1

    def get_grid_position(self, pos, positions): #计算格子 
        min_dist = 100000000  # 初始化一个很大的距离
        min_pos = -1  # 初始化最小距离的位置
        for i, square_center_pos in enumerate(positions):
            dist = np.linalg.norm(np.array(square_center_pos) - np.array(pos))  # 计算位置间的欧几里得距离
            if dist < min_dist:  # 找到最近的格子
                min_pos = i
                min_dist = dist
        
        # 将平面坐标转换为棋盘格子的索引 (i, j)
        return (min_pos // 3, min_pos % 3)


    def check_winner(self):
        # 检查行和列
        for i in range(3):
            if self.board[i, 0] == self.board[i, 1] == self.board[i, 2] != 0:
                return self.board[i, 0]
            if self.board[0, i] == self.board[1, i] == self.board[2, i] != 0:
                return self.board[0, i]

        # 检查对角线
        if self.board[0, 0] == self.board[1, 1] == self.board[2, 2] != 0:
            return self.board[0, 0]
        if self.board[0, 2] == self.board[1, 1] == self.board[2, 0] != 0:
            return self.board[0, 2]

        return 0  # 没有获胜者

    def is_full(self):
        return not any(0 in row for row in self.board)

    def minimax(self, depth, is_maximizing):
        winner = self.check_winner()
        if winner != 0 or self.is_full():
            if winner == 1: return 10 - depth
            elif winner == -1: return depth - 10
            else: return 0

        if is_maximizing:
            max_eval = -float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i, j] == 0:
                        self.board[i, j] = -1
                        eval = self.minimax(depth + 1, False)
                        self.board[i, j] = 0
                        max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i, j] == 0:
                        self.board[i, j] = 1
                        eval = self.minimax(depth + 1, True)
                        self.board[i, j] = 0
                        min_eval = min(min_eval, eval)
            return min_eval

    def best_move(self):
        best_val = -float('inf')
        move = (-1, -1)
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:
                    self.board[i, j] = -1
                    move_val = self.minimax(0, False)
                    self.board[i, j] = 0
                    if move_val > best_val:
                        move = (i, j)
                        best_val = move_val
        return move

    def make_move(self, player):
        if player == -1:
            move = self.best_move()
            if move != (-1, -1):
                self.board[move[0], move[1]] = -1

# def main():
#     cap = cv2.VideoCapture(0)
#     vis = vision()
#     calibration = HandInEyeCalibration()
#     control = Control()
#     game = TicTacToe()

#     # 机器先手在中间
#     game.board[1, 1] = -1

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         edges = vis.process_img(frame)
#         rect = vis.get_chessboard_coordinates(edges)
#         frame, positions = vis.draw_grid_numbers_and_get_positions(frame, rect)
#         frame, piece_coordinates, black_piece_positions, white_piece_positions = vis.detect_and_mark_pieces(frame, positions)
        
#         game.update_board(piece_coordinates)
#         winner = game.check_winner()
#         if winner != 0:
#             print(f"Player {winner} wins!")
#             break

#         # 机器的回合
#         if not game.is_full():
#             game.make_move(-1)
#             winner = game.check_winner()
#             if winner != 0:
#                 print(f"Player {winner} wins!")
#                 break

#         cv2.imshow('TicTacToe', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == '__main__':
#     main()

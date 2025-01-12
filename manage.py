#coding=utf-8
# 用于棋盘状态管理
import cv2
import numpy as np
from visual import vision
from transform import HandInEyeCalibration
from control import Control

class TicTacToe:
    def __init__(self):
        self.board = np.zeros((3, 3), dtype=int)  # 初始化棋盘矩阵为全0
        self.player_color = 'black'
        self.machine_color = 'white'
    
    def update_board(self, piece_coordinates):
        self.board.fill(0)  # 清空棋盘
        for color, positions in piece_coordinates.items():
            for pos in positions:
                i, j = self.get_grid_position(pos)
                if color == self.player_color:
                    self.board[i, j] = 1  # 人类标志位为1
                elif color == self.machine_color:
                    self.board[i, j] = -1  # 机器标志位为-1

    def get_grid_position(self, pos):
        # 根据中心点坐标，计算棋盘矩阵的位置
        x, y = pos
        cell_size = 3  # 每个格子的大小
        i = y // cell_size
        j = x // cell_size
        return i, j

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
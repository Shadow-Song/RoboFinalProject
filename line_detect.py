import cv2
import numpy as np
import servo as sv
import time


class PathDetection:
    # 打开视频流
    cap = cv2.VideoCapture(0)
    next_path = 0  # 0 for forward, 1 for left, 2 for right
    color_area = 0
    selected_color = None

    lower = [[110, 100, 100], [35, 70, 50], [110, 50, 50], [0, 0, 0], [20, 100, 100]]
    upper = [[10, 255, 255], [85, 255, 255], [130, 255, 255], [180, 255, 30], [30, 255, 255]]

    def __init__(self, selected_color):
        self.selected_color = selected_color

    def read_frame(self):
        _, frame = self.cap.read()

        # 转换到HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 定义蓝色的HSV范围
        lower_blue = np.array(self.lower[self.selected_color])
        upper_blue = np.array(self.upper[self.selected_color])
        # 创建蓝色的掩码
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # 使用掩码获取蓝色区域
        blue_area = cv2.bitwise_and(frame, frame, mask=mask)

        # 计算蓝色区域的面积
        blue_area_gray = cv2.cvtColor(blue_area, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(blue_area_gray, 1, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.color_area = sum(cv2.contourArea(contour) for contour in contours)

    def run(self):
        
import math
# import time

import cv2
import numpy as np
from sklearn.cluster import KMeans
import warnings

COLLINEAR = 0
CLOCKWISE = 1
COUNTERCLOCKWISE = 2

# set flags for direction
straight = False
left = False
right = False

center = [320, 240]

threshold = 90
threshold_straight = 15
threshold_straight_single = 180

# ignore the warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def detect_blue_lines(image):
    """
    Detect the blue lines. Analyze and process images
    :param image: the processed image
    :return: None
    """
    global center

    # turn the image into HSV from BGR
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义蓝色范围
    lower_blue = np.array([100, 80, 100])
    upper_blue = np.array([130, 200, 255])

    # 根据蓝色范围创建掩码
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # 在原始图像上应用掩码
    result = cv2.bitwise_and(image, image, mask=mask)

    # 将结果图像转换为灰度图
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    # 使用霍夫变换检测直线
    lines = cv2.HoughLinesP(gray, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is not None:
        # merge the lines
        merged_lines = merge_similar_lines(np.squeeze(lines, axis=1))

        # check if there is only one line
        try:
            merged_lines = check_lines(merged_lines)
        except IndexError:
            pass

        # 在原始图像上绘制合并后的直线
        for line in merged_lines:
            x1, y1, x2, y2 = line.astype(int)
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if len(merged_lines) == 1:
            # calculate the angle
            line1 = find_line_equation(merged_lines[0])
            angle1 = angle_with_vertical_line(line1[0])
            # show the angles on the screen
            text1 = "angle1: %.2f" % angle1
            cv2.putText(image, text1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 0, 255), 2, cv2.LINE_AA)
            # judge direction
            judge_direction_single_line(merged_lines, angle1, center)
            # print the possible directions on the screen
            show_direction(image)
            # print the distance
            if merged_lines[0][1] > merged_lines[0][3]:
                temp_point = [merged_lines[0][2], merged_lines[0][3]]
                distance_to_corner(image, temp_point)
            else:
                temp_point = [merged_lines[0][0], merged_lines[0][1]]
                distance_to_corner(image, temp_point)

        elif len(merged_lines) >= 2:
            try:
                # find the intersection
                line1 = find_line_equation(merged_lines[0])
                line2 = find_line_equation(merged_lines[1])
                intersection = find_intersection_point(line1, line2)

                # show the intersection on the screen
                if intersection is not None:
                    draw_intersection(image, intersection)

                # calculate the angle
                angle1 = angle_with_vertical_line(line1[0])
                angle2 = angle_with_vertical_line(line2[0])
                # show the angles on the screen
                text1 = "angle1: %.2f" % angle1
                text2 = "angle2: %.2f" % angle2
                cv2.putText(image, text1, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(image, text2, (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2, cv2.LINE_AA)

                # judge direction
                judge_direction(merged_lines, angle1, angle2, intersection)
                # print the possible directions on the screen
                show_direction(image)
                # print the distance
                distance_to_corner(image, intersection)
            except IndexError:
                pass

    # 显示结果图像
    cv2.imshow('Detected Blue Lines', image)


def merge_similar_lines(lines, angle_threshold=10):
    """
    Merge similar lines based on their angles using K-means clustering
    :param lines: array of lines
    :param angle_threshold: threshold for merging lines with similar angles (default: 10 degrees)
    :return: array (containing the merged lines)
    """
    # Calculate the angles of each line
    angles = np.degrees(np.arctan2(lines[:, 3] - lines[:, 1], lines[:, 2] - lines[:, 0]))

    # If there are not enough samples, skip this function and return the original lines
    if len(lines) <= 2:
        return lines

    # Apply K-means clustering to group lines based on their angles
    kmeans = KMeans(n_clusters=2).fit(angles.reshape(-1, 1))

    # Get the labels assigned by the clustering algorithm
    labels = kmeans.labels_

    # Merge lines in the same cluster
    merged_lines = []
    for label in np.unique(labels):
        cluster_lines = lines[labels == label]

        # Calculate the mean line as the merged line
        merged_line = np.mean(cluster_lines, axis=0)
        merged_lines.append(merged_line)

    return np.array(merged_lines)


def check_lines(merged_lines):
    # 计算第一条直线的斜率和截距
    slope1, intercept1 = find_line_equation(merged_lines[0])
    # 计算第二条直线的斜率和截距
    slope2, intercept2 = find_line_equation(merged_lines[1])
    # 计算两条直线与竖直线之间的角度差
    temp = angle_with_vertical_line(slope1) - angle_with_vertical_line(slope2)
    # 如果角度差的绝对值小于等于30度
    if abs(temp) <= 30:
        # 删除第二条直线
        merged_lines = np.delete(merged_lines, 1, axis=0)

    return merged_lines


def find_intersection(lines):
    """
    Find the intersection of lines
    :param lines: array of lines
    :return: array (containing the coordinates of the intersection points)
    """
    x1, y1, x2, y2 = lines[0]
    x3, y3, x4, y4 = lines[1]

    # the function of line1 is: Ax + By + C = 0
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2

    # the function of line2 is: Dx + Ey + F = 0
    D = y4 - y3
    E = x3 - x4
    F = x4 * y3 - x3 * y4

    determinant = A * E - B * D

    if determinant == 0:
        # lines are parallel with no intersection
        return None
    else:
        x = (C * E - B * F) / determinant
        y = (A * F - C * D) / determinant
        intersection = np.array([x, y])
        print(intersection)
        return intersection


def orientation(p, q, r):
    """
    Calculate the orientation of three points: p, q, and r
    :param p: first point (tuple of x,y coordinates)
    :param q: second point (tuple of x,y coordinates)
    :param r: third point (tuple of x,y coordinates)
    :return: COLLINEAR if the points are collinear,
             CLOCKWISE if the points form a clockwise orientation,
             COUNTERCLOCKWISE if the points form a counterclockwise orientation
    """
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return COLLINEAR  # points are collinear
    return CLOCKWISE if val > 0 else COUNTERCLOCKWISE  # clockwise or counterclockwise


def find_line_equation(line):
    # 计算直线的斜率和截距

    x1, y1, x2, y2 = line

    # 处理斜率为无穷大的情况
    if x1 == x2:
        slope = float('inf')
        intercept = x1  # 截距即为 x 坐标值
    else:
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1

    return slope, intercept


def find_intersection_point(line1, line2):
    # 解方程组求解交点
    slope1, intercept1 = line1
    slope2, intercept2 = line2
    # slope1, intercept1, slope2, intercept2 = line

    if slope1 == slope2:
        # 两直线平行，没有交点
        return None
    else:
        # 计算交点坐标
        x = (intercept2 - intercept1) / (slope1 - slope2)
        y = slope1 * x + intercept1
        return x, y


def draw_intersection(image, intersection):
    """
    Draw the intersection on the screen
    :param image: the processed image
    :param intersection: coordinates of the intersection point
    :return: None
    """
    try:
        x = int(intersection[0])
        y = int(intersection[1])
        if x > 0 and y > 0:
            cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
    except ValueError:
        pass


def angle_with_vertical_line(slope):
    # 计算与垂直线的角度的tan值
    tan_value = -1 / slope

    # 计算角度
    angle_rad = math.atan(tan_value)

    # 将弧度转换为角度
    angle_deg = math.degrees(angle_rad)

    return angle_deg


def calculate_distance(point1, point2):
    """
    Calculate the distance between two points
    :param point1: the xy-coordinate value of point 1
    :param point2: the xy-coordinate value of point 2
    :return: distance
    """
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def set_default_direction_flags():
    global straight, left, right
    straight = False
    left = False
    right = False


def judge_direction(lines, angle1, angle2, intersection):
    global straight, left, right

    set_default_direction_flags()

    # check the first line
    line1 = lines[0]
    point1 = [line1[0], line1[1]]
    point2 = [line1[2], line1[3]]

    if abs(angle1) <= 45:
        # go straight might be possible
        # determine the distance from the two endpoints to the point of intersection
        distance1 = calculate_distance(point1, intersection)
        distance2 = calculate_distance(point2, intersection)

        if distance1 > threshold_straight and distance2 > threshold:
            straight = True
    else:
        # turn left or right might be possible
        # determine the distance from the two endpoints to the point of intersection
        distance1 = calculate_distance(point1, intersection)
        distance2 = calculate_distance(point2, intersection)

        if distance1 >= threshold and point1[0] < intersection[0]:
            left = True
        elif distance1 >= threshold and point1[0] > intersection[0]:
            right = True

        if distance2 >= threshold and point2[0] < intersection[0]:
            left = True
        elif distance2 >= threshold and point2[0] > intersection[0]:
            right = True

    # check the second line
    # if angle2 and lines[1]:
    line2 = lines[1]
    point3 = [line2[0], line2[1]]
    point4 = [line2[2], line2[3]]

    if abs(angle2) <= 45:
        # go straight might be possible
        # determine the distance from the two endpoints to the point of intersection
        distance1 = calculate_distance(point3, intersection)
        distance2 = calculate_distance(point4, intersection)

        if distance1 > threshold_straight and distance2 > threshold:
            straight = True
    else:
        # turn left or right might be possible
        # determine the distance from the two endpoints to the point of intersection
        distance1 = calculate_distance(point3, intersection)
        distance2 = calculate_distance(point4, intersection)

        if distance1 >= threshold and point3[0] < intersection[0]:
            left = True
        elif distance1 >= threshold and point3[0] > intersection[0]:
            right = True

        if distance2 >= threshold and point4[0] < intersection[0]:
            left = True
        elif distance2 >= threshold and point4[0] > intersection[0]:
            right = True


def judge_direction_single_line(lines, angle1, point):
    global straight, left, right

    set_default_direction_flags()

    # check the first line
    line1 = lines[0]
    point1 = [line1[0], line1[1]]
    point2 = [line1[2], line1[3]]

    if abs(angle1) <= 45:
        # go straight might be possible
        # determine the distance of the two end points
        distance = calculate_distance(point1, point2)
        print(distance)
        if distance > threshold_straight_single:
            straight = True


def show_direction(image):
    global straight, left, right

    if straight or left or right:
        if straight:
            cv2.putText(image, "Straight is possible", (10, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 0, 255), 2, cv2.LINE_AA)
        if left:
            cv2.putText(image, "Left is possible", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 0, 255), 2, cv2.LINE_AA)
        if right:
            cv2.putText(image, "Right is possible", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 0, 255), 2, cv2.LINE_AA)

    else:
        cv2.putText(image, "Stop", (10, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 0, 255), 2, cv2.LINE_AA)


def distance_to_corner(image, point):
    """
    Calculate the distance from the point to the corner, and show it on the screen
    :param image: the screen
    :param point: array
    :return: None
    """
    distance = 480 - point[1]
    text = "distance: %.2f" % distance
    cv2.putText(image, text, (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 0, 255), 2, cv2.LINE_AA)

import cv2 as cv
import numpy as np
from cv2 import VideoCapture
import drive
import time

ref = False
driver = drive.Driver()
MAX_SPEED = 20
time_l = 0
time_r = 0
time_s = 0


class Point:
    """ class Point for points
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


def show_lines() -> VideoCapture:
    """ This function will show out the camera and blue lines in it.
    """
    global ref
    capture = get_camera()  # get camera

    while True:
        ref, frame = capture.read()  # get the picture of camera.

        # process the frame to get the edges of image
        edges = process_image(frame)
        lines = cv.HoughLinesP(edges, 1, np.pi / 180, 70, maxLineGap=500)  # get the lines in finial picture

        # the shape is the height (0) and width (1)
        width = frame.shape[1]
        height = frame.shape[0]
        min_height = height * 0.3  # look at 70% to the bottom of the height.
        max_height = height
        min_width = width * 0.3  # look at 30% to the left of the center.
        max_width = width * 0.7  # look at 30% to the right of the center.

        # traverse the lines.
        try:
            new_lines = []  # new_lines will store lines
            i = 0  # "i" remembers the number of lines
            results = []  # results will store the slopes of lines
            points = []  # points will store the points in the camera.

            # get the lines, lines' slopes and points.
            for line in lines:
                new_lines.append(line[0])
                x1, y1, x2, y2 = line[0]
                A = Point(x1, y1)
                B = Point(x2, y2)
                points.append((A, B))
                result = slope(x1, y1, x2, y2)
                results.append(result)
                i = i + 1

            # catch and print lines
            for j in range(i):
                x1, y1, x2, y2 = new_lines[j]
                result = results[j]
                average_x = int((x1 + x2) / 2)
                average_y = int((y1 + y2) / 2)

                # compare other lines to choose the correct line to print
                for r in range(i):
                    int_result = int(results[j])  # current line
                    int_results = int(results[r])  # other line
                    if ((int_result - int_results) < 30) & ((int_result - int_results) > -30) & (j != r) & (
                            int_result != 1000):
                        if int_result <= 45:  # if the line is horizontal
                            if points[j][0].y > points[r][0].y:  # get the lower line
                                results[r] = 1000
                        if int_result > 45:  # if the line is vertical
                            if points[j][0].x > points[r][0].x:  # get the righter line
                                results[r] = 1000
                        results[j] = 1000

                # set it to catch the lines only in specific area.
                if (min_width < average_x < max_width) & (min_height < average_y < max_height) & (results[j] != 1000):
                    # show the angle of lines, and divide the horizontal lines if it means turn left and right.
                    if 0 <= result < 45:  # if the line is horizontal
                        for n in range(i):
                            if (results[n] == 1000) | (j == n):  # give up the useless lines
                                continue
                            # if it is a long horizontal line which means turn left and right.
                            if (points[j][0].x < (points[n][0].x - 30)) & (points[j][1].x > (points[n][0].x + 30)):
                                cv.putText(frame, str(round(90 - result, 1)), (points[j][1].x, points[j][1].y), 0, 0.5,
                                           (255, 255, 255), 1, cv.LINE_AA)
                                cv.putText(frame, str(-round(90 - result, 1)), (points[j][0].x, points[j][0].y), 0, 0.5,
                                           (255, 255, 255), 1, cv.LINE_AA)
                            else:  # if it is not a long horizontal line.
                                cv.putText(frame, str(round(90 - result, 1)), (average_x, average_y), 0, 0.5,
                                           (255, 255, 255), 1, cv.LINE_AA)
                    if result >= 45:  # if the line is vertical.
                        cv.putText(frame, str(round(90 - result, 1)), (average_x, average_y), 0, 0.5, (255, 255, 255),
                                   1, cv.LINE_AA)
                    if -45 <= result < 0:  # if the line is horizontal
                        for m in range(i):
                            if (results[m] == 1000) | (j == m):  # give up the useless lines
                                continue
                            # if it is a long horizontal line which means turn left and right.
                            if (points[j][0].x < (points[m][0].x - 50)) & (points[j][1].x > (points[m][0].x + 50)):
                                cv.putText(frame, str(round(-90 - result, 1)), (points[j][1].x, points[j][1].y), 0,
                                           0.5, (255, 255, 255), 1, cv.LINE_AA)
                                cv.putText(frame, str(-round(-90 - result, 1)), (points[j][0].x, points[j][0].y), 0,
                                           0.5, (255, 255, 255), 1, cv.LINE_AA)
                            else:  # if it is not a long horizontal line.
                                cv.putText(frame, str(round(-90 - result, 1)), (average_x, average_y), 0, 0.5,
                                           (255, 255, 255), 1, cv.LINE_AA)
                    if result < -45:  # if the line is vertical.
                        cv.putText(frame, str(round(-90 - result, 1)), (average_x, average_y), 0, 0.5, (255, 255, 255),
                                   1, cv.LINE_AA)

                    # print lines
                    cv.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)

            point = Point(0, 0)  # set the initial value of intersection.
            a = 0  # a flag to check if an intersection has be found.
            for h in range(i):
                if results[h] == 1000:  # give up the useless lines
                    continue
                for n in range(i):  # when road is "end" or "straight", the top point will be seen as a junction
                    if i <= 2:
                        x = int(points[h][1].x)
                        y = int(points[h][1].y)
                        if (results[h] > 45) & (results[n] != 1000):
                            print(results[h])
                            cv.circle(frame, (x, y), 3, (0, 0, 255), 1, 3)
                            cv.putText(frame, "junction(virtual):", (30, 20), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
                            cv.putText(frame, str(round(2 * ((height - y) / height), 2)), (30, 40), 0, 0.5,
                                       (255, 255, 255), 1, cv.LINE_AA)
                            a = 1
                    # if i <= 2:
                    #     x = int(points[h][1].x)
                    #     y = int(points[h][1].y)
                    #     if (results[h] < -45) & (results[n] != 1000):
                    #         print(results[h])
                    #         cv.circle(frame, (x, y), 3, (0, 0, 255), 1, 3)
                    #         cv.putText(frame, "junction(virtual):", (30, 20), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
                    #         cv.putText(frame, str(round(2 * ((height - y) / height), 2)), (30, 40), 0, 0.5,
                    #                    (255, 255, 255), 1, cv.LINE_AA)
                            a = 1
                    if (results[n] == 1000) | (h == n):
                        continue
                    # check if these two lines are intersected.
                    if (0 < results[h] < 45) | (-45 < results[h] <= 0):
                        points[h][1].x = points[h][1].x + 20
                    if (0 < results[n] < 45) | (-45 < results[n] <= 0):
                        points[n][1].x = points[n][1].x + 20
                    if doIntersect(points[h][0], points[h][1], points[n][0], points[n][1]):
                        if a == 0:
                            # print the junctions and details.
                            point = lineLineIntersection(points[h][0], points[h][1], points[n][0], points[n][1])
                            cv.circle(frame, (int(point.x), int(point.y)), 3, (0, 0, 255), 1, 3)
                            cv.putText(frame, "junction:", (30, 20), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
                            cv.putText(frame, str(round(2 * ((height - point.y) / height), 2)), (30, 40), 0, 0.5,
                                       (255, 255, 255), 1, cv.LINE_AA)
                            a = 1
                    if (0 < results[h] < 45) | (-45 < results[h] <= 0):
                        points[h][1].x = points[h][1].x - 20
                    if (0 < results[n] < 45) | (-45 < results[n] <= 0):
                        points[n][1].x = points[n][1].x - 20

            # check what type of the road it is
            road_type(i, points, results, point, frame)

        # if it has a typeError
        except TypeError:
            c = cv.waitKey(1) & 0xff
            if c == 27:
                break

        # cv.imshow("1", frame)  # show the frame picture.

        # close the camera when press 'esc'.
        c = cv.waitKey(1) & 0xff
        if c == 27:
            break

    return capture


def process_image(frame):
    """ Process the picture to get the edges of the picture by getting hsv, mixture and gray type of picture
    """
    img = cv.cvtColor(frame, cv.COLOR_BGR2HSV)  # get the hsv mode of picture
    # get the blue part of picture.
    lower_blue = np.array([64, 100, 100])
    upper_blue = np.array([124, 255, 255])
    mask = cv.inRange(img, lower_blue, upper_blue)

    result = cv.bitwise_and(frame, frame, mask=mask)  # get the mixture of initial picture and mask
    gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)  # ture the picture to gray color.
    edges = cv.Canny(gray, 100, 200)  # get the edges of the picture.
    return edges


def road_type(i: int, points: list, results: list, point: Point, frame):
    """ check what type of the road it is
    """
    global time_s
    global time_l
    global time_r
    tag = [0, 0, 0, 0]  # a tag to store what the road it is.
    for m in range(i):
        if results[m] == 1000:  # give up the useless lines
            continue
        # if it has a line straight.
        if ((point.y - points[m][1].y) > 50) | (((points[m][0].y - points[m][1].y) > 100) & (i <= 2)):
            cv.putText(frame, "straight", (30, 100), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
            tag[0] = 1
        elif ((points[m][1].y - point.y ) > 50) | ((( points[m][1].y - points[m][0].y ) > 100) & (i <= 2)):
            cv.putText(frame, "straight", (30, 100), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
            tag[0] = 1
        # if it has a left choice
        if ((point.x - points[m][0].x) > 50) & (point.x != 0):
            cv.putText(frame, "left", (30, 60), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
            tag[1] = 1
        # if it has a right choice
        if ((points[m][1].x - point.x) > 50) & (point.x != 0):
            cv.putText(frame, "right", (30, 80), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
            tag[2] = 1
        # if it is a line end
        if ((points[m][0].y - points[m][1].y) < 50) & (i <= 2):
            cv.putText(frame, "end", (30, 120), 0, 0.5, (255, 255, 255), 1, cv.LINE_AA)
            tag[3] = 1

    # according to the tag,  print out what type of road it is
    if (tag[0] == 1) & (tag[1] == tag[2] == tag[3] == 0):
        print("It is straight line, it has a single path – forwards.")
        for a in range(i):
            if results[a] == 1000:  # give up the useless lines
                continue
            if (((point.y - points[a][1].y) > 50) | (((points[a][0].y - points[a][1].y) > 100) & (i <= 2))) | ((points[m][1].y - point.y ) > 50) | ((( points[m][1].y - points[m][0].y ) > 100) & (i <= 2)):
                print('Go Straight')
                if time_s <2:
                    time_s += 1
                    break
                if results[a] > 0:
                    print(30*(results[a]/90))
                    driver.drive(30, 30*(results[a]/90))
                if results[a] < 0:
                    print(results[a]/90)
                    driver.drive(-30*(results[a]/90), 30)
                time_s += 1
                if time_s >= 2:
                    time_r = 0
                    time_l = 0

    elif (tag[1] == tag[2] == 1) & (tag[0] == tag[3] == 0):
        print("It is a terminating T-junction, it has two paths, left and right.")
    elif (tag[0] == tag[1] == 1) & (tag[2] == tag[3] == 0):
        print("It is a left T-junction, it has 2 paths, left and forwards.")
        for b in range(i):
            if results[b] == 1000:  # give up the useless lines
                continue
            if ((point.x - points[b][0].x) > 50) & (point.x != 0):
                print("Go Left")
                if time_l > 1:
                    driver.drive(0, MAX_SPEED)
                    time_s = 0
                elif time_l <= 1 :
                    driver.drive(10, 10)
                    print(time_l)
                time_l += 1
    elif (tag[0] == tag[2] == 1) & (tag[1] == tag[3] == 0):
        print("It is a right T-junction, it has 2 paths, right and forwards.")
    elif (tag[1] == 1) & (tag[0] == tag[2] == tag[3] == 0):
        print("It is a left corner, it has only 1 path, left.")
        for b in range(i):
            if results[b] == 1000:  # give up the useless lines
                continue
            if ((point.x - points[b][0].x) > 50) & (point.x != 0):
                print("Go Left")
                if time_l > 1:
                    driver.drive(0, MAX_SPEED)
                    time_s = 0
                elif time_l <= 1 :
                    driver.drive(10, 10)
                    print(time_l)
                time_l += 1
    elif (tag[2] == 1) & (tag[0] == tag[1] == tag[3] == 0):
        print("It is a right corner, it has only 1 path, right.")
        for c in range(i):
            if results[c] == 1000:  # give up the useless lines
                continue
            if ((points[c][1].x - point.x) > 50) & (point.x != 0):
                print('Go Right')
                if time_r > 1:
                    driver.drive(MAX_SPEED, 0)
                    time_s = 0
                elif time_r <= 1:
                    driver.drive(10, 10)
                    print(time_r)
                time_r += 1
    elif (tag[0] == tag[1] == tag[2] == 1) & (tag[3] == 0):
        print("It is a crossroads, it has 3 paths, left, forwards and right.")
    elif (tag[3] == 1) & (tag[0] == tag[1] == tag[2] == 0):
        print("It is a line end, it does not have any paths.")


def get_camera():
    """ get camera
    """
    capture = cv.VideoCapture(0)  # open the computer camera.
    # if the camera cannot be opened, print something.
    if not capture.isOpened():
        print("Cannot open camera")
        exit()
    return capture


def slope(x1: int, y1: int, x2: int, y2: int) -> int:
    """ get the slope of a line by getting its beginning point and end point
    """
    # change the type of x1, y1, x2, y2.
    x1 = float(x1)
    x2 = float(x2)
    y1 = float(y1)
    y2 = float(y2)
    if x2 - x1 == 0:
        result = 90
    elif y2 - y1 == 0:
        result = 0
    else:
        # calculate slope
        k = -(y2 - y1) / (x2 - x1)
        # turn to angle
        num = np.arctan(k) * 57.29577
        result = num
    return result


def onSegment(p: Point, q: Point, r: Point) -> bool:
    """ check if p , q and r are collinear and r lies on segment pq
    """
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
            (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p: Point, q: Point, r: Point):
    """ to find the orientation of an ordered triplet (p,q,r)
        function returns the following values:
        0 : Collinear points
        1 : Clockwise points
        2 : Counterclockwise
    """

    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if val > 0:

        # Clockwise orientation
        return 1
    elif val < 0:

        # Counterclockwise orientation
        return 2
    else:

        # Collinear orientation
        return 0


def doIntersect(p1: Point, q1: Point, p2: Point, q2: Point) -> bool:
    """ The main function that returns true if the line segment 'p1q1' and 'p2q2' intersect.
    """
    # Find the 4 orientations required for
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases

    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if (o1 == 0) and onSegment(p1, p2, q1):
        return True

    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if (o2 == 0) and onSegment(p1, q2, q1):
        return True

    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if (o3 == 0) and onSegment(p2, p1, q2):
        return True

    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if (o4 == 0) and onSegment(p2, q1, q2):
        return True

    # If none of the cases
    return False


def lineLineIntersection(a: Point, b: Point, c: Point, d: Point) -> Point:
    """ get the junction of two lines
    """
    # Line AB represented as a1x + b1y = c1
    a1 = b.y - a.y
    b1 = a.x - b.x
    c1 = a1 * a.x + b1 * a.y

    # Line CD represented as a2x + b2y = c2
    a2 = d.y - c.y
    b2 = c.x - d.x
    c2 = a2 * c.x + b2 * c.y

    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        # The lines are parallel. This is simplified
        # by returning a pair of FLT_MAX
        return Point(10 ** 9, 10 ** 9)
    else:
        x = (b2 * c1 - b1 * c2) / determinant
        y = (a1 * c2 - a2 * c1) / determinant
        return Point(x, y)


if __name__ == '__main__':
    capture = show_lines()  # use method show_lines

    capture.release()  # release the space
    cv.destroyAllWindows()  # close the windows

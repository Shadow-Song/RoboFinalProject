import cv2 as cv
import numpy as np
from cv2 import VideoCapture
import drive
import log
import servo as sv
import camera
import cancel_button as cb

ref = False
driver: drive.Driver = None
logger: log.Logger = None
lens: camera.Camera = None
MAX_SPEED = 40
time_l = -1
time_r = 0
time_s = 0
f = 0

lower = [
    [64, 100, 100],
    [0, 90, 90],
    [35, 70, 50],
    [0, 0, 0],
    [20, 100, 100]
]
upper = [
    [124, 255, 255],
    [10, 255, 255],
    [85, 255, 255],
    [180, 255, 70],
    [30, 255, 255]
]

color_index: int = None

def init(drive: drive.Driver, logging: log.Logger, max_speed: float, color: int, camera: camera.Camera):
    global MAX_SPEED
    global color_index
    global driver
    global logger
    global lens

    servo = sv.Servo(0)
    servo.write(0)
    driver = drive
    logger = logging
    lens = camera

    MAX_SPEED = max_speed
    color_index = color

def run():
    global color_index
    print(f'Color Index: {color_index}')
    capture = show_lines()

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
    global time_l
    global logger
    capture = get_camera()  # get camera

    while True:
        ref, frame = capture.read()  # get the picture of camera.

        # process the frame to get the edges of image
        edges = process_image(frame)
        lines = cv.HoughLinesP(edges, 1, np.pi / 180, 70, maxLineGap=500)  # get the lines in finial picture

        # the shape is the height (0) and width (1)
        height = frame.shape[0]
        min_height = height *0  # look at 70% to the bottom of the height.
        max_height = height
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
                # (min_width < average_x < max_width)&
                if (min_height < average_y < max_height) & (results[j] != 1000):
                    # show the angle of lines, and divide the horizontal lines if it means turn left and right.
                    if 0 <= result < 45:  # if the line is horizontal
                        for n in range(i):
                            if (results[n] == 1000) | (j == n):  # give up the useless lines
                                continue
                            # if points[j][0].y < points[n][1].y:
                            #     continue
                            # if it is a long horizontal line which means turn left and right.
                            if (points[j][0].x < (points[n][0].x - 30)):
                                time_l =0
                            elif(points[j][1].x > (points[n][0].x + 30)):
                                time_l = 1
                            # print(time_l)
                    if result >= 45:  # if the line is vertical.
                        if (200< points[j][0].x<400) & (200< points[j][1].x<400):
                            if points[j][0].x < 300:
                                error = 1- (300 - points[j][0].x)/300
                                driver.drive(MAX_SPEED * error, MAX_SPEED)
                                # print(35 * error,"--------", 35)
                            if points[j][0].x > 300:
                                error = 1- (points[j][0].x - 300)/300
                                driver.drive(MAX_SPEED, MAX_SPEED * error)
                                # print(35 ,"--------", 35* error)
                        if ((400< points[j][0].x) & (400< points[j][1].x))|((200< points[j][0].x<400) & (400< points[j][1].x)) | (( points[j][0].x<200) & (200< points[j][1].x<400)):
                            driver.drive(40,10)
                        if ((points[j][0].x<200) & (points[j][1].x<200)) | ((points[j][0].x<200) & (200< points[j][1].x<400)) | ((200< points[j][0].x<400) & ( points[j][1].x>400)):
                            driver.drive(10,40)
                    if -45 <= result < 0:  # if the line is horizontal
                        for m in range(i):
                            if (results[m] == 1000) | (j == m):  # give up the useless lines
                                continue
                            # if it is a long horizontal line which means turn left and right.
                            if (points[j][0].x < (points[m][0].x - 30)):
                                time_l = 0
                            elif(points[j][1].x > (points[m][0].x + 30)):
                                time_l = 1
                            # print(time_l)
                    if result < -45:  # if the line is vertical.
                        if (200< points[j][0].x<400) & (200< points[j][1].x<400):
                            if points[j][0].x < 300:
                                error = 1- (300 - points[j][0].x)/300
                                # TODO
                                driver.drive(MAX_SPEED * error, MAX_SPEED)
                                # print(35 * error,"--------", 35)
                            if points[j][0].x > 300:
                                error = 1- (points[j][0].x - 300)/300
                                driver.drive(35, 35 * error)
                                # print(35 ,"--------", 35* error)
                        if ((400< points[j][0].x) & (400< points[j][1].x))|((200< points[j][0].x<400) & (400< points[j][1].x)) | (( points[j][0].x<200) & (200< points[j][1].x<400)):
                            driver.drive(40,10)
                        if ((points[j][0].x<200) & (points[j][1].x<200)) | ((points[j][0].x<200) & (200< points[j][1].x<400)) | ((200< points[j][0].x<400) & ( points[j][1].x>400)):
                            driver.drive(10,40)

                    # print lines
                    cv.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)

        # if it has a typeError
        except TypeError:
            if time_l == 0:
                # print("left")
                driver.drive(-30, 30)
                logger.write('Decision, turn left.', 0)
                logger.write('Left: -30 -- Right: 30', 1)
                # time.sleep(1.25)
                time_l=-1
            if time_l == 1:
                # print("right")
                driver.drive(30, -30)
                logger.write('Decision, turn right.', 0)
                logger.write('Left: 30 -- Right: -30', 1)
                # time.sleep(1.25)
                time_l = -1
            c = cv.waitKey(1) & 0xff
            if c == 27:
                break

        # cv.imshow("1", frame)  # show the frame picture.

        # close the camera when press 'esc'.
        cb.jump_out()

    return capture

def process_image(frame):
    global color_index
    """ Process the picture to get the edges of the picture by getting hsv, mixture and gray type of picture
    """
    img = cv.cvtColor(frame, cv.COLOR_BGR2HSV)  # get the hsv mode of picture
    # get the blue part of picture.
    lower_blue = np.array(lower[color_index])
    upper_blue = np.array(upper[color_index])
    mask = cv.inRange(img, lower_blue, upper_blue)

    result = cv.bitwise_and(frame, frame, mask=mask)  # get the mixture of initial picture and mask
    gray = cv.cvtColor(result, cv.COLOR_BGR2GRAY)  # ture the picture to gray color.
    edges = cv.Canny(gray, 100, 200)  # get the edges of the picture.
    return edges

def get_camera():
    """ get camera
    """
    global lens
    capture = lens.cap # open the computer camera.
    # if the camera cannot be opened, print something.
    if not capture.isOpened():
        # print("Cannot open camera")
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

if __name__ == '__main__':
    
    logger = log.Logger(0)
    driver = drive.Driver(logger=logger)
    init(
        drive=driver,
        logging=logger,
        max_speed=30,
        color=0
    )
    run()

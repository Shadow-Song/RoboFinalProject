import RPi.GPIO as GPIO
import time
import pyzbar.pyzbar as pyzbar
import cv2
import threading
import servo as sv
import drive
import camera

class Ultrasound:

    driver = None
    servo = None
    lens = None
    MAX_SPEED = None
    TRIG = 20
    ECHO = 21
    reaction_distance = None

    servoMin = 150  # Min pulse length out of 4096
    servoMax = 600  # Max pulse length out of 4096

    width = 0
    height = 0
    result = None
    w1 = 300
    h1 = 300
    x1 = 0
    y1 = 0

    new_code = ''
    code_list = ['']

    def __init__(self, driver, camera, max_speed, reaction_distance):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        self.driver = driver
        self.servo = sv.Servo(0)
        self.lens = camera
        self.MAX_SPEED = max_speed
        self.reaction_distance = reaction_distance

    def capture(self):
        i = 0
        self.servo.write(90)
        width, height = self.lens.get_size()
        self.x1 = int(width / 2 - self.w1 / 2)
        self.y1 = int(height / 2 - self.h1 / 2)
        if not self.lens.is_open():
            print('Camera not detected.')
            return
        while True:
            ret, img = self.lens.get_frame()
            if not ret:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.show_code_string(gray=gray, image=img)

            if not self.append_code(new_code=self.new_code):
                self.driver.t_stop(2)

                cv2.imwrite(f'./img/img{i}.jpg', img)
                print(f'Image {i} saved.')
                self.code_list.append(self.new_code)
                i += 1

            key = cv2.waitKey(5)
            if key == 27:
                break

    def show_code_string(self, gray, image):
        code_strings = pyzbar.decode(gray)
        for code_string in code_strings:
            (x, y, w, h) = code_string.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            if x >= self.x1 and y >= self.y1 and x + w <= self.x1 + self.w1 and y + h <= self.y1 + self.h1:
                self.result = True
            else:
                self.result = False

            self.new_code = code_string.data.decode('utf-8')
            code_type = code_string.type
            print("[INFO] Found {} barcode: {}".format(code_type, self.new_code))

    def append_code(self, new_code):
        return new_code in self.code_list


    def get_distance(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.output(self.TRIG, 0)
        time.sleep(0.000002)

        GPIO.output(self.TRIG, 1)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, 0)

        
        while GPIO.input(self.ECHO) == 0:
            a = 0
        time1 = time.time()
        while GPIO.input(self.ECHO) == 1:
            a = 1
        time2 = time.time()

        during = time2 - time1
        return during * 340 / 2 * 100

    def measure(self, angle):
        self.servo.write(angle)
        time.sleep(0.5)
        distance = self.get_distance()
        return distance
    
    def detection(self):
        while True:
            distance_front = self.measure(90)
            if distance_front < self.reaction_distance:
                self.driver.t_stop(0.2)
                self.driver.t_back(15, 0.3)
                self.driver.t_stop(0.2)
                distance_left = self.measure(175)
                distance_right = self.measure(5)

                if distance_left < 40 and distance_right < 40:
                    self.driver.t_left(15, 0.7)

                elif distance_left > distance_right:
                    self.driver.t_left(15, 0.7)
                    self.driver.t_stop(0.5)
                else:
                    self.driver.t_right(15, 0.7)
                    self.driver.t_stop(0.5)
            else:
                self.driver.t_forward(self.MAX_SPEED, 0)

    @staticmethod
    def destory():
        GPIO.cleanup()

    def run(self):
        thread1 = threading.Thread(target=self.capture)
        thread2 = threading.Thread(target=self.detection)

        thread1.start()
        thread2.start()

        try:
            thread1.join()
            thread2.join()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            Ultrasound.destroy()

if __name__ == '__main__':
    driver = drive.Driver()
    lens = camera.Camera()
    ultrasound = Ultrasound(driver=driver, camera=lens, max_speed=40, reaction_distance=30)
    ultrasound.run()


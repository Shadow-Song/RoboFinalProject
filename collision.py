import RPi.GPIO as GPIO
import time
import threading
import servo as sv
import drive
import camera

class Ultrasound:

    driver: drive.Driver = None
    servo: sv.Servo = None
    lens: camera.Camera = None
    MAX_SPEED = None
    TRIG = 20
    ECHO = 21
    reaction_distance = None

    servoMin = 150  # Min pulse length out of 4096
    servoMax = 600  # Max pulse length out of 4096

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
            distance_front = self.measure(35)
            self.detected(distance_front=distance_front)
            time.sleep(0.2)
            distance_front = self.measure(90)
            self.detected(distance_front=distance_front)
            time.sleep(0.2)
            distance_front = self.measure(145)
            self.detected(distance_front=distance_front)
            time.sleep(0.2)
            

    def detected(self, distance_front):
        if distance_front < self.reaction_distance:
            self.servo.write(90)
            self.driver.t_stop(0.2)
            self.driver.t_back(30, 0.3)
            self.driver.t_stop(0.2)
            distance_left = self.measure(175)
            distance_right = self.measure(5)

            if distance_left < 40 and distance_right < 40:
                self.driver.t_left(15, 0.7)

            elif distance_left > distance_right:
                self.driver.t_left(30, 0.7)
                self.driver.t_stop(0.5)
            else:
                self.driver.t_right(30, 0.7)
                self.driver.t_stop(0.5)
        else:
            self.driver.t_forward(self.MAX_SPEED, 0)

    @staticmethod
    def destory():
        GPIO.cleanup()

    def run(self):
        thread1 = threading.Thread(target=self.lens.capture_QR)
        thread2 = threading.Thread(target=self.detection)

        thread1.start()
        thread2.start()

        try:
            thread1.join()
            thread2.join()
        except KeyboardInterrupt:
            Ultrasound.destroy()

if __name__ == '__main__':
    driver = drive.Driver()
    lens = camera.Camera()
    ultrasound = Ultrasound(driver=driver, camera=lens, max_speed=20, reaction_distance=30)
    ultrasound.run()


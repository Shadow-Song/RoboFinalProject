import RPi.GPIO as GPIO
import drive
import log

class IRTracer:
    T_SensorLeft = 13
    T_SensorMid = 19
    T_SensorRight = 26
    ir_sensor_pins= [T_SensorLeft, T_SensorMid, T_SensorRight]

    driver: drive.Driver = None
    logger: log.Logger = None

    MAX_SPEED = None

    left_servo_speed: int
    right_servo_speed: int

    ir_sensors = 0b000
    error = 0
    error_last = 0

    def __init__(self, max_speed: int, driver: drive.Driver, logger: log.Logger):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.T_SensorRight, GPIO.IN)
        GPIO.setup(self.T_SensorLeft, GPIO.IN)
        GPIO.setup(self.T_SensorMid, GPIO.IN)

        self.MAX_SPEED = max_speed
        self.left_servo_speed = self.MAX_SPEED
        self.right_servo_speed = self.MAX_SPEED
        self.driver = driver
        self.logger = logger

    def scan(self):
        self.ir_sensors = 0b000
        for i in range(3):
            sensor_value = GPIO.input(self.ir_sensor_pins[i])
            b = 2 - i
            self.ir_sensors = self.ir_sensors + (sensor_value << b)

    def update_direfction(self):
        self.error_last = self.error

        if self.ir_sensors == 0b000:
            if self.error_last < 0:
                self.error = -self.MAX_SPEED
            elif self.error_last > 0:
                self.error = self.MAX_SPEED
        elif self.ir_sensors == 0b100:
            self.logger.write('Shift Left Fast.', 0)
            self.error = -40
        elif self.ir_sensors == 0b110:
            self.logger.write('Shift Left Slowly.', 0)
            self.error = -35
        elif self.ir_sensors == 0b010:
            self.logger.write('Movie Forward.', 1)
            self.error = 0
        elif self.ir_sensors == 0b011:
            self.logger.write('Shift Right Slowly.', 0)
            self.error = 35
        elif self.ir_sensors == 0b001:
            self.logger.write('Shift Right Fast.', 0)
            self.error = 40
        elif self.ir_sensors == 0b111:
            self.logger.write('I\'m Blocked!', 0)
            self.error = 0
        else: # 0b101
            self.error = 0

        if self.error >= 0:
            self.left_servo_speed = self.MAX_SPEED
            self.right_servo_speed = self.MAX_SPEED - self.error
        elif self.error < 0:
            self.left_servo_speed = self.MAX_SPEED + self.error
            self.right_servo_speed = self.MAX_SPEED
    
    def run(self):
        try:
            while True:
                self.scan()
                self.update_direfction()
                self.driver.drive(self.left_servo_speed, self.right_servo_speed)

        except KeyboardInterrupt:
            GPIO.cleanup()

if __name__ == '__main__':
    driver = drive.Driver()
    ir = IRTracer(speed_rate=0.75, driver=driver)
    ir.run()

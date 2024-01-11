import RPi.GPIO as GPIO
import time
import log

class Driver:
    PWMB = 18
    BIN2 = 27
    BIN1 = 22
    
    PWMA = 23
    AIN2 = 24
    AIN1 = 25
    L_Motor = None
    R_Motor = None

    logger: log.Logger = None

    def __init__(self, logger):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.PWMA, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.PWMB, GPIO.OUT)

        self.logger = logger
        self.L_Motor = GPIO.PWM(self.PWMA, 100)
        self.L_Motor.start(0)
        self.R_Motor = GPIO.PWM(self.PWMB, 100)
        self.R_Motor.start(0)

    def set_motor(self, left_speed, right_speed, reverse_L, reverse_R):
        self.L_Motor.ChangeDutyCycle(left_speed)
        GPIO.output(self.AIN1, reverse_L)  # AIN2
        GPIO.output(self.AIN2, not reverse_L)  # AIN1
        self.R_Motor.ChangeDutyCycle(right_speed)
        GPIO.output(self.BIN1, reverse_R)  # BIN2
        GPIO.output(self.BIN2, not reverse_R)  # BIN1

    def drive(self, left, right):
        self.logger.write(f'LeftSpeed: {left} -- RightSpeed: {right}', 1)
        reverse_L = True
        reverse_R = True
        if left < 0:
            left = -left
            reverse_L = False
        if right < 0:
            right = -right
            reverse_R = False
        self.set_motor(left, right, reverse_L, reverse_R)

    def t_forward(self, speed, t_time):
        self.logger.write(f'Forward on {speed}, {t_time}second(s).', 0)
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.AIN2, False)#AIN2
        GPIO.output(self.AIN1, True) #AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.BIN2, False)#BIN2
        GPIO.output(self.BIN1, True) #BIN1
        time.sleep(t_time)
        
    def t_stop(self, t_time):
        self.logger.write(f'Stop {t_time}second(s).', 0)
        self.L_Motor.ChangeDutyCycle(0)
        GPIO.output(self.AIN2, False)#AIN2
        GPIO.output(self.AIN1, False) #AIN1

        self.R_Motor.ChangeDutyCycle(0)
        GPIO.output(self.BIN2, False)#BIN2
        GPIO.output(self.BIN1, False) #BIN1
        time.sleep(t_time)
        
    def t_back(self, speed, t_time):
        self.logger.write(f'Go Back on {speed}, {t_time}second(s).', 0)
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.AIN2, True)#AIN2
        GPIO.output(self.AIN1, False) #AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.BIN2, True)#BIN2
        GPIO.output(self.BIN1, False) #BIN1
        time.sleep(t_time)

    def t_left(self, speed, t_time):
        self.logger.write(f'Shift left {speed}, {t_time}second(s).', 0)
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.AIN2, True)#AIN2
        GPIO.output(self.AIN1, False) #AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.BIN2, False)#BIN2
        GPIO.output(self.BIN1, True) #BIN1
        time.sleep(t_time)

    def t_right(self, speed, t_time):
        self.logger.write(f'Shift on {speed}, {t_time}second(s).', 0)
        self.L_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.AIN2, False)#AIN2
        GPIO.output(self.AIN1, True) #AIN1

        self.R_Motor.ChangeDutyCycle(speed)
        GPIO.output(self.BIN2, True)#BIN2
        GPIO.output(self.BIN1, False) #BIN1
        time.sleep(t_time)
    
if __name__ == '__main__':
    driver = Driver()

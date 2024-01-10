import pylirc, time, pygame
import RPi.GPIO as GPIO
import drive
import servo

class Controller:
    BtnPin = 19
    Gpin = 5
    Rpin = 6

    blocking = 0
    driver = None
    servo_z = servo.Servo(1)
    servo_y = servo.Servo(2)

    def __init__(self, driver: drive.Driver):
        self.driver = driver
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Rpin, GPIO.OUT)
        GPIO.setup(self.BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def keyscan(self):
        val = GPIO.input(self.BtnPin)
        while GPIO.input(self.BtnPin) == False:
            val = GPIO.input(self.BtnPin)
        while GPIO.input(self.BtnPin) == True:
            time.sleep(0.01)
            val = GPIO.input(self.BtnPin)
            if val == True:
                GPIO.output(self.Rpin, 1)
                while GPIO.input(self.BtnPin) == False:
                    GPIO.output(self.Rpin, 0)
            else:
                GPIO.output(self.Rpin, 0)

    def IR(self, config):
        if config == 'KEY_CHANNEL':
            self.driver.t_forward(50, 0)
            print ('t_up')
        if config == 'KEY_NEXT':
            self.driver.t_stop(0)
            print ('t_stop')
        if config == 'KEY_PREVIOUS':
            self.driver.t_left(50, 0)
            print ('t_left')
        if config == 'KEY_PLAYPAUSE':
            self.driver.t_right(50, 0)
            print ('t_right')
        if config == 'KEY_VOLUMEUP':
            self.driver.t_back(50, 0)
            print ('t_down')

    def loop(self):
        while True:
            s = pylirc.nextcode(1)
            while(s):
                for (code) in s:
                    for (code) in s:
                        print ('Command: ', code["config"])
                        self.IR(code["config"])
                    if(not self.blocking):
                        s = pylirc.nextcode(1)
                    else:
                        s = []

    @staticmethod
    def destory():
        GPIO.cleanup()
        pylirc.exit()

    def run(self):
        self.keyscan()
        pylirc.init('pylirc', 'conf', self.blocking)
        try:
            self.loop()
        except KeyboardInterrupt:
            self.destory()


class DualShock4:

    joystick = None
    driver = None
    MAX_SPEED: int

    left_speed = 0
    right_speed = 0
    break_flag = False

    y_value = 0
    z_value = 90

    servo_z = servo.Servo(1)
    servo_y = servo.Servo(2)

    def __init__(self, driver: drive.Driver, max_speed: int):
        self.driver = driver
        self.joystick = self.init_joystick()
        self.MAX_SPEED = max_speed

    def init_joystick(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("No joystick/gamepad found!")
            return None
        else:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"Initialized joystick: {joystick.get_name()}")
            return joystick
        
    def update_value(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 10:
                    return True
                if event.button == 1:
                    if self.left_speed == 40:
                        continue
                    else:
                        self.left_speed = self.left_speed + 10
                        self.right_speed = self.right_speed + 10
                    print(f'{self.left_speed} -- {self.right_speed}')
                if event.button == 0:
                    if self.left_speed == -40:
                        continue
                    else:
                        self.left_speed = self.left_speed - 10
                        self.right_speed = self.right_speed - 10
                    print(f'{self.left_speed} -- {self.right_speed}')
                if event.button == 3:
                    print('Stop')
                    self.left_speed = 0
                    self.right_speed = 0
                    self.break_flag = True
                if event.button == 4:
                    print('Shifting Left...')
                    self.left_speed = 0 - (self.MAX_SPEED / 2)
                    self.right_speed = (self.MAX_SPEED / 2)
                if event.button == 5:
                    print('Shifting Right...')
                    self.left_speed = self.MAX_SPEED / 2
                    self.right_speed = 0 - (self.MAX_SPEED / 2)

            if event.type == pygame.JOYAXISMOTION and not self.break_flag:
                if event.axis == 5 and event.value > -1:
                    print('Forward')
                    self.left_speed = self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                    self.right_speed = self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                if event.axis == 2 and event.value > -1:
                    print('Back')
                    self.left_speed = 0 - self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                    self.right_speed = 0 - self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                if event.value < -1:
                    break

            if event.type == pygame.JOYBUTTONUP:
                if event.button == 3:
                    print("free")
                    self.break_flag = False
                if event.button == 7:
                    print('7 free')
                    self.left_speed = 0
                    self.right_speed = 0                    
                if event.button == 6:
                    print('6 free')
                    self.left_speed = 0
                    self.right_speed = 0
                if event.button == 4:
                    print('Stop Shifing Left.')
                    self.left_speed = 0
                    self.right_speed = 0
                if event.button == 5:
                    print('Stop Shifing Right.')
                    self.left_speed = 0
                    self.right_speed = 0

            if event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_x == -1:
                    if self.z_value == 150:
                        continue
                    else:
                        self.z_value = self.z_value + 15
                elif hat_x == 1:
                    if self.z_value == 30:
                        continue
                    else:
                        self.z_value = self.z_value - 15
                elif hat_y == 1:
                    if self.y_value == 90:
                        continue
                    else:
                        self.y_value = self.y_value + 15
                elif hat_y == -1:
                    if self.y_value == 0:
                        continue
                    else:
                        self.y_value = self.y_value - 15
                

    def run(self):
        while True:
            stop = self.update_value()
            time.sleep(0.02)
            self.driver.drive(self.left_speed, self.right_speed)
            self.servo_y.write(self.y_value)
            self.servo_z.write(self.z_value)
            if stop:
                break
        pygame.quit()


if __name__ ==  '__main__':
    driver = drive.Driver()
    controller = DualShock4(driver=driver, max_speed=30)
    controller.run()


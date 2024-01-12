import pylirc, time, pygame
import RPi.GPIO as GPIO
import drive
import servo
import camera
import log
import cancel_button as cb

class IRController:
    BtnPin = 19
    Gpin = 5
    Rpin = 6
    blocking = 0

    driver: drive.Driver = None
    MAX_SPEED: int = None
    lens: camera.Camera = None
    logger: log.Logger = None

    servo_z = servo.Servo(1)
    servo_y = servo.Servo(2)

    def __init__(self, driver: drive.Driver, max_speed: int, logger: log.Logger):
        self.driver = driver
        self.MAX_SPEED = max_speed
        self.logger = logger
        self.lens = camera.Camera(logger=self.logger)
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
    driver: drive.Driver = None
    lens: camera.Camera = None
    MAX_SPEED: int = None
    logger: log.Logger

    left_speed = 0
    right_speed = 0
    break_flag = False

    y_value = 0
    z_value = 90

    servo_z = servo.Servo(1)
    servo_y = servo.Servo(2)

    def __init__(self, driver: drive.Driver, max_speed: int, logger: log.Logger):
        self.driver = driver
        self.logger = logger
        self.lens = camera.Camera(logger=self.logger)
        self.joystick = self.init_joystick()
        self.MAX_SPEED = max_speed

    def init_joystick(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print(f"No joystick/gamepad found!")
            raise KeyboardInterrupt
        else:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"Initialized joystick: {joystick.get_name()}")
            self.logger.write(f"Initialized joystick: {joystick.get_name()}", 0)
            return joystick
        
    def update_value(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 10:
                    # PS Button: Exit
                    return True
                if event.button == 1:
                    # Circle Button: Speed Up
                    if self.left_speed == 40:
                        continue
                    else:
                        self.logger.write('Speed Up.', 0)
                        self.left_speed = self.left_speed + 10
                        self.right_speed = self.right_speed + 10
                    # print(f'{self.left_speed} -- {self.right_speed}')
                if event.button == 0:
                    # Cross Button: Speed Down
                    if self.left_speed == -40:
                        continue
                    else:
                        self.logger.write('Speed Down.', 0)
                        self.left_speed = self.left_speed - 10
                        self.right_speed = self.right_speed - 10
                    print(f'{self.left_speed} -- {self.right_speed}')
                if event.button == 2:
                    # Triangle Button: Capture
                    self.lens.capture()
                if event.button == 3:
                    # Square Button: Break
                    print('Stop')
                    self.logger.write('Break Pressed.', 0)
                    self.left_speed = 0
                    self.right_speed = 0
                    self.break_flag = True
                if event.button == 4:
                    # L1 Button: Shift Left
                    # print('Shifting Left...')
                    self.left_speed = 0 - (self.MAX_SPEED / 2)
                    self.right_speed = (self.MAX_SPEED / 2)
                if event.button == 5:
                    # R1 Button: Shift Right
                    # print('Shifting Right...')
                    self.left_speed = self.MAX_SPEED / 2
                    self.right_speed = 0 - (self.MAX_SPEED / 2)

            if event.type == pygame.JOYAXISMOTION and not self.break_flag:
                # Right Trigger: Forward
                if event.axis == 5 and event.value > -1:
                    self.left_speed = self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                    self.right_speed = self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                    self.logger.write(f'Moving Forward on {self.MAX_SPEED * (round(event.value, 3)+1) * 0.5}', 1)
                # Left Trigger: Back
                if event.axis == 2 and event.value > -1:
                    self.left_speed = 0 - self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                    self.right_speed = 0 - self.MAX_SPEED * (round(event.value, 3)+1) * 0.5
                    self.logger.write(f'Moving Backward on {self.MAX_SPEED * (round(event.value, 3)+1) * 0.5}', 1)
                if event.value < -1:
                    break

            if event.type == pygame.JOYBUTTONUP:
                if event.button == 3:
                    # Square Button: Break Release
                    print("free")
                    self.logger.write('Break Released.', 0)
                    self.break_flag = False
                if event.button == 7 or event.button == 6 or event.button == 4 or event.button == 5:
                    # L1, L2, R1, R2 Released, Stop
                    self.left_speed = 0
                    self.right_speed = 0
                    self.logger.write('Speed Button Released.', 0)

            if event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_x == -1:
                    # Camera Left
                    if self.z_value == 150:
                        continue
                    else:
                        self.z_value = self.z_value + 15
                        self.logger.write('Camera Turing Left.', 0)
                elif hat_x == 1:
                    # Camera Right
                    if self.z_value == 30:
                        continue
                    else:
                        self.z_value = self.z_value - 15
                        self.logger.write('Camera Turing Right.', 0)
                elif hat_y == 1:
                    # Camera Up
                    if self.y_value == 90:
                        continue
                    else:
                        self.y_value = self.y_value + 15
                        self.logger.write('Camera Turing Up.', 0)
                elif hat_y == -1:
                    # Camera Down
                    if self.y_value == 0:
                        continue
                    else:
                        self.y_value = self.y_value - 15
                        self.logger.write('Camera Turing Down.', 0)

    def run(self):
        while True:
            stop = self.update_value()
            time.sleep(0.02)
            self.driver.drive(self.left_speed, self.right_speed)
            self.servo_y.write(self.y_value)
            self.servo_z.write(self.z_value)
            self.lens.run()
            cb.jump_out()
            if stop:
                break
        pygame.quit()


if __name__ ==  '__main__':
    driver = drive.Driver()
    lens = camera.Camera()
    controller = DualShock4(driver=driver, camera=lens, max_speed=30)
    controller.run()


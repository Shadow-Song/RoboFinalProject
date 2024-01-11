import RPi.GPIO as GPIO
import time
import ir_tracing as ir
import drive
import controller
import collision
import camera
import identify_path

class Menu:
    # Device constants
    ButtonA = 17
    ButtonB = 20
    ButtonC = 21

    LCD_RS = 5  # Pi pin 26
    LCD_E = 4  # Pi pin 24
    LCD_D4 = 25  # Pi pin 22
    LCD_D5 = 24  # Pi pin 18
    LCD_D6 = 23  # Pi pin 16
    LCD_D7 = 18  # Pi pin 12

    select = None
    confirm = None
    cancel = None

    LCD_CHR = True  # Character mode
    LCD_CMD = False  # Command mode
    LCD_CHARS = 16  # Characters per line (16 max)
    LCD_LINE_1 = 0x80  # LCD memory location for 1st line
    LCD_LINE_2 = 0xC0  # LCD memory location 2nd line
    MAX_SPEED = 60

    # Mark Current Selection
    selected_mode = -1
    selected_setting = -1
    selected_settings = [0, 0, 0, 0, 0]

    # Available Options
    setting_options = [
        # 'Light',
        'Line Color',
        'Max Speed',
        # 'Image Size',
        'Distance',
        # 'Collision',
        'Logging',
        'Run'
    ]

    # Available Modes
    mode_options = [
        'IR Tracing',
        'Camera Tracing',
        'Free Travel',
        'Remote Control'
    ]

    setting_content = [
        # ['on', 'off', 'auto'],
        ['blue', 'red', 'green', 'black', 'yellow'],
        ['25%', '50%', '75%', '100%'],
        # ['640x480', '1280x720', '1920x1080'],
        ['10cm', '20cm', '30cm', '40cm', '50cm', '1m'],
        # ['Stop', 'Back up', 'Turn Around'],
        ['Disabled', 'Minimal', 'Extensive'],
        ['IR Controller', 'DualShock 4'],
    ]

    speed_value = [0.25, 0.5, 0.75, 1]
    distance_value = [10, 20, 30, 40, 50, 100]
    MAX_SPEED = 40

    # Available Settings
    available_settings = [
        [1, 3, 4],
        [0, 1, 3, 4],
        [1, 2, 3, 4],
        [1, 3, 4, 5]
    ]

    ir_tracer = None
    driver = None
    controller = None
    ultrasound = None
    lens = None

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
        GPIO.setup(self.LCD_E, GPIO.OUT)  # Set GPIO's to output mode
        GPIO.setup(self.LCD_RS, GPIO.OUT)
        GPIO.setup(self.LCD_D4, GPIO.OUT)
        GPIO.setup(self.LCD_D5, GPIO.OUT)
        GPIO.setup(self.LCD_D6, GPIO.OUT)
        GPIO.setup(self.LCD_D7, GPIO.OUT)
        GPIO.setup(self.ButtonA, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(self.ButtonB, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(self.ButtonC, GPIO.IN, GPIO.PUD_UP)
        # GPIO.setup(self.ButtonD, GPIO.IN, GPIO.PUD_UP)
        self.select = GPIO.input(self.ButtonA)
        self.confirm = GPIO.input(self.ButtonB)
        self.cancel = GPIO.input(self.ButtonC)
        # Initialize display
        self.lcd_init()

    # Menu Level 1
    def menu_1(self):
        var = 0
        while True:
            self.lcd_text('Mode', self.LCD_LINE_1)
            self.lcd_text('> ' + self.mode_options[var], self.LCD_LINE_2)
            time.sleep(0.2)
            key = self.wait_key()
            if key == 0:
                if var == len(self.mode_options) - 1:
                    var = 0
                else:
                    var += 1
            elif key == 1:
                self.selected_mode = var
                self.menu_2()

    # Menu Level 2
    def menu_2(self):
        var = 0
        while True:
            self.lcd_text(self.mode_options[self.selected_mode], self.LCD_LINE_1)
            self.lcd_text('> ' + self.setting_options[self.available_settings[self.selected_mode][var]], self.LCD_LINE_2)
            time.sleep(0.2)
            key = self.wait_key()
            if key == 0:
                if var == len(self.available_settings[self.selected_mode]) - 1:
                    var = 0
                else:
                    var += 1
            elif key == 1:
                print(var)
                if self.available_settings[self.selected_mode][var] == len(self.setting_options)-1:
                    self.run()
                    return
                self.selected_setting = self.available_settings[self.selected_mode][var]
                self.menu_3()
            elif key == 2:
                return

    # Menu Level 3
    def menu_3(self):
        var = 0
        while True:
            self.lcd_text(self.setting_options[self.selected_setting],
                          self.LCD_LINE_1)
            self.lcd_text('> ' + self.setting_content[self.selected_setting][var], self.LCD_LINE_2)
            time.sleep(0.2)
            key = self.wait_key()
            if key == 0:
                if var == len(self.setting_content[self.selected_setting]) - 1:
                    var = 0
                else:
                    var += 1
            elif key == 1:
                self.selected_settings[self.selected_setting] = var
                return
            elif key == 2:
                return

    def lcd_init(self):
        self.lcd_write(0x33, self.LCD_CMD)  # Initialize
        self.lcd_write(0x32, self.LCD_CMD)  # Set to 4-bit mode
        self.lcd_write(0x06, self.LCD_CMD)  # Cursor move direction
        self.lcd_write(0x0C, self.LCD_CMD)  # Turn cursor off
        self.lcd_write(0x28, self.LCD_CMD)  # 2 line display
        self.lcd_write(0x01, self.LCD_CMD)  # Clear display
        time.sleep(0.0005)  # Delay to allow commands to process

    def lcd_write(self, bits, mode):
        # High bits
        GPIO.output(self.LCD_RS, mode)  # RS
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(self.LCD_D4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(self.LCD_D5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(self.LCD_D6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

        # Low bits
        GPIO.output(self.LCD_D4, False)
        GPIO.output(self.LCD_D5, False)
        GPIO.output(self.LCD_D6, False)
        GPIO.output(self.LCD_D7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(self.LCD_D4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(self.LCD_D5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(self.LCD_D6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(self.LCD_D7, True)

        # Toggle 'Enable' pin
        self.lcd_toggle_enable()

    def lcd_toggle_enable(self):
        time.sleep(0.0005)
        GPIO.output(self.LCD_E, True)
        time.sleep(0.0005)
        GPIO.output(self.LCD_E, False)
        time.sleep(0.0005)

    def lcd_text(self, message, line):
        # Send text to display
        message = message.ljust(self.LCD_CHARS, " ")
        self.lcd_write(line, self.LCD_CMD)
        for i in range(self.LCD_CHARS):
            self.lcd_write(ord(message[i]), self.LCD_CHR)

    # Wait for button press
    def wait_key(self) -> int:
        while True:
            self.select = GPIO.input(self.ButtonA)
            self.confirm = GPIO.input(self.ButtonB)
            self.cancel = GPIO.input(self.ButtonC)
            if self.select == True:
                print("Select Pressed.")
                return 0
            elif self.confirm == True:
                print("Confirm Pressed.")
                return 1
            elif self.cancel == True:
                print("Cancel Pressed.")
                return 2

    # Run selected mode
    def run(self):
        self.driver = drive.Driver()
        if self.selected_mode == 0:
            self.ir()
        elif self.selected_mode == 1:
            self.camera()
        elif self.selected_mode == 2:
            self.free_travel()
        elif self.selected_mode == 3:
            self.controller_run()

    def ir(self):
        print("IR Running...")
        self.ir_tracer = ir.IRTracer(self.speed_value[self.selected_settings[1]], self.driver)
        self.ir_tracer.run()

    def free_travel(self):
        print("Free Travel Running...")
        self.lens = camera.Camera()
        self.ultrasound = collision.Ultrasound(
            driver=self.driver,
            camera=self.lens, 
            max_speed=self.MAX_SPEED*self.speed_value[self.selected_settings[1]], 
            reaction_distance=self.distance_value[self.selected_settings[2]]
        )
        self.ultrasound.run()


    def controller_run(self):
        print("Remote Controll Running...")
        if self.selected_settings[4] == 0:
            self.controller = controller.IRController(
                driver=self.driver, 
                max_speed=self.MAX_SPEED*self.speed_value[self.selected_settings[1]]
            )
        else:
            self.controller = controller.DualShock4(
                driver=self.driver, 
                max_speed=self.MAX_SPEED*self.speed_value[self.selected_settings[1]]
            )
        self.controller.run()

    def camera(self):
        print("Camera Travel Running...")
        identify_path.init(
            rate=self.speed_value[self.selected_settings[1]],
            color=self.selected_settings[0]
        )

if __name__ == '__main__':
    menu = Menu()
    menu.menu_1()
    # menu.lcd_text("Hello", menu.LCD_LINE_1)
    # time.sleep(10)

from Adafruit_PWM_Servo_Driver import PWM
import time

class Servo:
    pwm = PWM(0x40,debug = False)
    name = None

    def __init__(self, name):
        self.pwm.setPWMFreq(50)
        self.name = name

    def setServoPulse(self, channel, pulse):
        pulseLength = 1000000.0                   # 1,000,000 us per second
        pulseLength /= 50.0                       # 60 Hz
        # print ("%d us per period" % pulseLength)
        pulseLength /= 4096.0                     # 12 bits of resolution
        # print ("%d us per bit" % pulseLength)
        pulse *= 1000.0
        pulse /= (pulseLength*1.0)
        # pwmV=int(pluse)
        # print ("pluse: %f  " % (pulse))
        self.pwm.setPWM(channel, 0, int(pulse))

    def write(self, x):
        y=x / 90.0 + 0.5
        y=max(y, 0.5)
        y=min(y, 2.5)
        self.setServoPulse(self.name, y)

if __name__ == '__main__':

    servo = Servo(1)
    
    while True:
        servo.write(0)
        time.sleep(1)
        servo.write(90)
        time.sleep(1)
        servo.write(180)
        time.sleep(1)
        servo.write(90)
        time.sleep(1)
    

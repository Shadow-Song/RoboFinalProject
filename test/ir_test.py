import pylirc, time
import RPi.GPIO as GPIO

BtnPin  = 19
Gpin    = 5
Rpin    = 6

blocking = 0

def keysacn():
    val = GPIO.input(BtnPin)
    while GPIO.input(BtnPin) == False:
        val = GPIO.input(BtnPin)
    while GPIO.input(BtnPin) == True:
        time.sleep(0.01)
        val = GPIO.input(BtnPin)
        if val == True:
            GPIO.output(Rpin,1)
            while GPIO.input(BtnPin) == False:
                GPIO.output(Rpin,0)
        else:
            GPIO.output(Rpin,0)


def IR(config):
        if config == 'KEY_CHANNEL':
                print ('t_up')
        if config == 'KEY_NEXT':
                print ('t_stop')
        if config == 'KEY_PREVIOUS':
                print ('t_left')
        if config == 'KEY_PLAYPAUSE':
                print ('t_right')
        if config == 'KEY_VOLUMEUP':
                print ('t_down')

def loop():
        while True:
                s = pylirc.nextcode(1)
                
                while(s):
                        for (code) in s:
                                print ('Command: ', code["config"] )
                                IR(code["config"])
                        if(not blocking):
                                s = pylirc.nextcode(1)
                        else:
                                s = []

def destroy():

	GPIO.cleanup()	
	pylirc.exit()

GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
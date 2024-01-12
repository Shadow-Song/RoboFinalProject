import RPi.GPIO as GPIO

def jump_out():
    cancel = GPIO.input(13)
    if cancel:
        raise KeyboardInterrupt
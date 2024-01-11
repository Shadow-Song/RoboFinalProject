import RPi.GPIO as GPIO

def jump_out():
    cancel = GPIO.input(21)
    if cancel:
        raise KeyboardInterrupt
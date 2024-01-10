#!/usr/bin/python

import pylirc, time
import RPi.GPIO as GPIO

Rpin = 17
Gpin = 18
Bpin = 27
blocking = 0

Lv = [100, 20, 90] # Light Level
color = [100, 100, 100]  #默认100时，占空比,100-100=0，是关闭灯

def setColor(color):
#	global p_R, p_G, p_B
	#更改占空比
	p_R.ChangeDutyCycle(100 - color[0])     # color[0]为控制红灯的颜色
	p_G.ChangeDutyCycle(100 - color[1])		# color[1]为控制绿灯的颜色
	p_B.ChangeDutyCycle(100 - color[2])		# color[2]为控制蓝灯的颜色

def setup():
	global p_R, p_G, p_B
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(Rpin, GPIO.OUT)
	GPIO.setup(Gpin, GPIO.OUT)
	GPIO.setup(Bpin, GPIO.OUT)
	
	p_R = GPIO.PWM(Rpin, 2000) # Set Frequece to 2KHz
	p_G = GPIO.PWM(Gpin, 2000)
	p_B = GPIO.PWM(Bpin, 2000)
	
	p_R.start(0)
	p_G.start(0)
	p_B.start(0)
	pylirc.init("pylirc", "./conf", blocking) #初始化lirc


def RGB(config):
	global color
	if config == 'KEY_CHANNELDOWN':
		color[0] = Lv[0]	#Lv[0]为=100,占空比为100-100=0，红灯灭
		print ('Red OFF')

	if config == 'KEY_CHANNEL':
		color[0] = Lv[1]	#Lv[1]为=20,占空比为100-20=80，红灯亮
		print ('Light Red')

	if config == 'KEY_CHANNELUP':
		color[0] = Lv[2]	#Lv[2]为=90,占空比为100-90=10，红灯暗
		print ('Red')

	if config == 'KEY_PREVIOUS':
		color[1] = Lv[0]	#Lv[0]为=100,占空比为100-100=0，绿灯灭
		print ('Green OFF')

	if config == 'KEY_NEXT':
		color[1] = Lv[1]	#Lv[1]为=20,占空比为100-20=80，绿灯亮
		print ('Light Green')

	if config == 'KEY_PLAYPAUSE':
		color[1] = Lv[2]	#Lv[2]为=90,占空比为100-90=10，绿灯暗
		print ('Green')

	if config == 'KEY_VOLUMEDOWN':
		color[2] = Lv[0]	#Lv[0]为=100,占空比为100-100=0，蓝灯灭
		print ('Blue OFF')

	if config == 'KEY_VOLUMEUP':
		color[2] = Lv[1]	#Lv[1]为=20,占空比为100-20=80，蓝灯亮
		print ('Light Blue')

	if config == 'KEY_EQUAL':
		color[2] = Lv[2]	#Lv[2]为=90,占空比为100-90=10，蓝灯暗
		print ('BLUE')

def loop():
	while True:
		s = pylirc.nextcode(1)
#如果初始化是ok的，您可以轮询lirc的命令。要读取队列中的任何命令，请调用pylirc.nextcode()
#如果队列中没有命令，或者列表中包含读取的命令，则returnvalue为'None'。
		while(s):
			for (code) in s:
#				print 'Command: ', code["config"] #For debug: Uncomment this
#				line to see the return value of buttons
				RGB(code["config"])
				setColor(color)
			if(not blocking):
				s = pylirc.nextcode(1)
			else:
				s = []

def destroy():
	p_R.stop()
	p_G.stop()
	p_B.stop()
	GPIO.output(Rpin, GPIO.LOW)    # Turn off all leds
	GPIO.output(Gpin, GPIO.LOW)
	GPIO.output(Bpin, GPIO.LOW)
	GPIO.cleanup()
	pylirc.exit()

if __name__ == '__main__':
	try:
		setup()
		loop()
	except KeyboardInterrupt:
		destroy()





#!/usr/bin/env python
from Adafruit_PWM_Servo_Driver import PWM
import RPi.GPIO as GPIO
import time
import sys
import pyzbar.pyzbar as pyzbar
import cv2
import threading

PWMA   = 18
AIN1   = 25
AIN2   = 24

PWMB   = 23
BIN1   = 22
BIN2   = 27

BtnPin  = 19
Gpin    = 5
Rpin    = 6

TRIG = 20
ECHO = 21
# Initialise the PWM device using the default address
# bmp = PWM(0x40, debug=True)
pwm = PWM(0x40,debug = False)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

width = 0
height = 0
result = ""
w1 = 300
h1 = 300
x1 = 0
y1 = 0
#barcodeDataNew = ""
#barcodeDataOld = ""
codeNew = ""
codeList = [""]

def decodeDisplay(image,image1):
    global result
    global x1
    global y1
    global codeNew
    # 下面是规定探测的区域的位置设置
    #x1 = int(width / 2 - w1 / 2)
    #y1 = int(height / 2 - h1 / 2)
        
    barcodes = pyzbar.decode(image)
    for barcode in barcodes:
        # 提取条形码的边界框的位置
        # 画出图像中条形码的边界框
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image1, (x, y), (x + w, y + h), (0, 0, 255), 2)
        if x >= x1 and y >= y1 and x + w <= x1 + w1 and y + h <= y1 + h1:
            result = "True"
        else:
            result = "Flase"
        
        # 条形码数据为字节对象，所以如果我们想在输出图像上
        # 画出来，就需要先将它转换成字符串
        codeNew = barcode.data.decode("utf-8") #二维码数据
        barcodeType = barcode.type   #二维码类型
 
        # 绘出图像上条形码的数据和条形码类型
        text = "{} ({})".format(codeNew, barcodeType)
        cv2.putText(image1, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    .5, (0, 0, 125), 2)
 
        # 向终端打印条形码数据和条形码类型
        print("[INFO] Found {} barcode: {}".format(barcodeType, codeNew))
    return image1

def detect():
    
    global width
    global height
    global x1
    global y1
    global result
    global w1
    global h1
    global barcodeDataNew
    #global barcodeDataOld
    i = 0
    write(1, 90)
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取视频的宽度
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 获取视频的高度
    x1 = int(width / 2 - w1 / 2)
    y1 = int(height / 2 - h1 / 2)
    if cap.isOpened() is True:  # 检查摄像头是否正常启动
        while True:
            # 读取当前帧
            ret, img = cap.read()
            if not ret:
                break
            # 转为灰度图像
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            im = decodeDisplay(gray,img)
            
            #在图像中显示True/False，并将限制区域标识出
            font = cv2.FONT_HERSHEY_SIMPLEX  # 设置字体样式
            cv2.putText(im, result, (10, 30), font, 1.0, (255, 0, 255), 2)
            cv2.rectangle(im, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 0), 2)  # frame要绘制的帧，四个坐标点，颜色，线宽
            if duplication_determine(codeNew) == False:
                t_stop(2)
                #if barcodeDataNew != barcodeDataOld:
                cv2.imwrite(r"c:\Users\mwjwj\Desktop\Pictures\\"+ str(i) + ".jpg",img) #存储路径
                print(f"Image {i} saved successfully.")
                i = i+1 
                codeList.append(codeNew)
                #barcodeDataOld = barcodeDataNew
            
            key = cv2.waitKey(5)
            # cv2.namedWindow('image', 0)
            # cv2.resizeWindow('image', 700, 500)
            # cv2.imshow("image", im)
            #barcodeDataOld = barcodeDataNew
            if key == 27:
                break
    else:
        print('cap is not opened!')
        
    #cap.release()
    #cv2.destroyAllWindows()


def duplication_determine(QRcode_new):
    number = len(codeList)
    determine = False
    for i in range(number):
        if QRcode_new == codeList[i]:
            determine = True
    return determine

def setServoPulse(channel, pulse):
  pulseLength = 1000000.0                   # 1,000,000 us per second
  pulseLength /= 50.0                       # 60 Hz
  #print("%d us per period" % pulseLength)
  pulseLength /= 4096.0                     # 12 bits of resolution
  #print("%d us per bit" % pulseLength)
  pulse *= 1000.0
  pulse /= (pulseLength*1.0)
# pwmV=int(pluse)
  print("pluse: %f  " % (pulse))
  pwm.setPWM(channel, 0, int(pulse))

#Angle to PWM
def write(servonum,x):
        y=x/90.0+0.5
        y=max(y,0.5)
        y=min(y,2.5)
        setServoPulse(servonum,y)
  
def t_up(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)#AIN2
        GPIO.output(AIN1,True) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)#BIN2
        GPIO.output(BIN1,False) #BIN1
        time.sleep(t_time)
        
def t_stop(t_time):
        L_Motor.ChangeDutyCycle(0)
        GPIO.output(AIN2,False)#AIN2
        GPIO.output(AIN1,False) #AIN1

        R_Motor.ChangeDutyCycle(0)
        GPIO.output(BIN2,False)#BIN2
        GPIO.output(BIN1,False) #BIN1
        time.sleep(t_time)
        
def t_down(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)#AIN2
        GPIO.output(AIN1,False) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)#BIN2
        GPIO.output(BIN1,True) #BIN1
        time.sleep(t_time)

def t_left(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,True)#AIN2
        GPIO.output(AIN1,False) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,True)#BIN2
        GPIO.output(BIN1,False) #BIN1
        time.sleep(t_time)

def t_right(speed,t_time):
        L_Motor.ChangeDutyCycle(speed)
        GPIO.output(AIN2,False)#AIN2
        GPIO.output(AIN1,True) #AIN1

        R_Motor.ChangeDutyCycle(speed)
        GPIO.output(BIN2,False)#BIN2
        GPIO.output(BIN1,True) #BIN1
        time.sleep(t_time) 
        
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
            
def setup():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        
        GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
        GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
        GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)

        GPIO.setup(AIN2,GPIO.OUT)
        GPIO.setup(AIN1,GPIO.OUT)
        GPIO.setup(PWMA,GPIO.OUT)
        
        GPIO.setup(BIN1,GPIO.OUT)
        GPIO.setup(BIN2,GPIO.OUT)
        GPIO.setup(PWMB,GPIO.OUT)
        pwm.setPWMFreq(50)                        # Set frequency to 60 Hz
        
def distance():
    GPIO.setmode(GPIO.BCM)
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    
    while GPIO.input(ECHO) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(ECHO) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def front_detection():
        write(0,90)
        time.sleep(0.5)
        dis_f = distance()
        return dis_f

def left_detection():
         write(0, 175)
         time.sleep(0.5)
         dis_l = distance()
         return dis_l
        
def right_detection():
        write(0,5)
        time.sleep(0.5)
        dis_r = distance()
        return dis_r
     
def ultrasound():
        while True:
                dis1 = front_detection()
                if (dis1 < 40) == True:
                        t_stop(0.2)
                        t_down(20,0.5)
                        t_stop(0.2)
                        dis2 = left_detection()
                        dis3 = right_detection()
                        if (dis2 < 40) == True and (dis3 < 40) == True:
                                t_left(20,1)
                        elif (dis2 > dis3) == True:
                                t_left(20,0.3)
                                t_stop(0.1)
                        else:
                                t_right(20,0.3)
                                t_stop(0.1)
                else:
                        t_up(30,0)
                #print('front:',dis1, 'cm')
                #print('')

def destroy():
    GPIO.cleanup()

if __name__ == "__main__":
        setup()
        L_Motor= GPIO.PWM(PWMA,100)
        L_Motor.start(0)
        R_Motor = GPIO.PWM(PWMB,100)
        R_Motor.start(0)
        #keysacn()
        thread1 = threading.Thread(target=detect)
        thread2 = threading.Thread(target=ultrasound)

        thread1.start()
        thread2.start()
        
        try:
                thread1.join()
                thread2.join()
        except KeyboardInterrupt:
                cv2.destroyAllWindows()
                destroy()


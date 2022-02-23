from picamera import PiCamera
from time import sleep
import os

camera = PiCamera()
camera.resolution = (64, 64)

camera.capture('/home/pi/Documents/code/image.jpg')
camera.close()
os.system("python3 /home/pi/Documents/code/camera_dones.py")




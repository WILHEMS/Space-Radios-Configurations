from picamera import PiCamera
from time import sleep


camera = PiCamera()
camera.resolution = (64, 64)
camera.start_preview()
sleep(5)
camera.capture('/home/pi/Documents/code/final/images/image.png')
camera.stop_preview()
camera.close()



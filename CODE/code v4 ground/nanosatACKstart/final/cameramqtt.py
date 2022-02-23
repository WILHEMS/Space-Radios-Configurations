from picamera import PiCamera
from time import sleep
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("Satellite/camera")

def on_message(client, userdata, msg):
    if msg.payload.decode() == "Take photo":
        camera = PiCamera()
        camera.resolution = (150, 150)
        camera.start_preview()
        sleep(2)
        camera.capture('/home/pi/Documents/code/final/images.jpg')
        camera.stop_preview()
        client.publish("Satellite/ImageTaken", "Done");
        print("Image has been taken")

client = mqtt.Client()
client.connect("localhost",1883,60)

client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()


import paho.mqtt.client as mqtt
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import Adafruit_ADS1x15  # Import the ADS1x15 module.
import time
from ubloxm8u import *


#added
import argparse
from datetime import datetime
from random import normalvariate
import struct
import sys
import time
import traceback
from uuid import UUID


import pigpio
from nrf24 import *
import pybase64
import sys








hostname = "localhost"
port = 8888
address = '1ACKS'

pi = pigpio.pi(hostname, port)
if not pi.connected:
    print("Not connected to Raspberry Pi ... goodbye.")
    sys.exit()

nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_1MBPS, pa_level=RF24_PA.MAX)
nrf.set_address_bytes(len(address))
nrf.set_retransmission(15, 15)
nrf.open_writing_pipe(address)
nrf.show_registers()

#end




'''def collectdata():
    print('collecting')
    # latitude, longitude, altitude, speed, heading_status = 0, 0, 0, 0, 0
    # Simple demo of reading each analog input from the ADS1x15 and printing it to
    # the screen.
    # Author: Tony DiCola
    # License: Public Domain

    # Create an ADS1115 ADC (16-bit) instance.
    adc = Adafruit_ADS1x15.ADS1115()

    # Note you can change the I2C address from its default (0x48), and/or the I2C
    # bus by passing in these optional parameters:
    # adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)

    # Choose a gain of 1 for reading voltages from 0 to 4.09V.
    # Or pick a different gain to change the range of voltages that are read:
    #  - 2/3 = +/-6.144V
    #  -   1 = +/-4.096V
    #  -   2 = +/-2.048V
    #  -   4 = +/-1.024V
    #  -   8 = +/-0.512V
    #  -  16 = +/-0.256V
    # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
    GAIN = 2 / 3

    print('Reading ADS1x15 values')
    # Print nice channel column headers.
    # print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
    # print('-' * 37)
    # Main loop.
    values = [0] * 4
    inputVoltage = (adc.read_adc(0, gain=GAIN))
    # while True:
    # Read all the ADC channel values in a list.

    # for i in range(4):
    #     # Read the specified ADC channel using the previously set gain value.
    #     values[i] = adc.read_adc(i, gain=GAIN)
    #     # Note you can also pass in an optional data_rate parameter that controls
    #     # the ADC conversion time (in samples/second). Each chip has a different
    #     # set of allowed data rate values, see datasheet Table 9 config register
    #     # DR bit values.
    #     #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
    #     # Each value will be a 12 or 16 bit signed integer value depending on the
    #     # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
    # Print the ADC values.
    # print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
    # Pause for half a second.
    # time.sleep(0.5)

    mpu = MPU9250(
        address_ak=AK8963_ADDRESS,
        address_mpu_master=MPU9050_ADDRESS_68,  # In 0x68 Address
        address_mpu_slave=None,
        bus=1,
        gfs=GFS_1000,
        afs=AFS_8G,
        mfs=AK8963_BIT_16,
        mode=AK8963_MODE_C100HZ)

    mpu.configure()  # Apply the settings to the registers.
    # print("Accelerometer", mpu.readAccelerometerMaster())
    # print("Gyroscope", mpu.readGyroscopeMaster())
    # print("Magnetometer", mpu.readMagnetometerMaster())
    # print("Temperature", mpu.readTemperatureMaster())
    # print("\n")
    accel = mpu.readAccelerometerMaster()
    gyro = mpu.readGyroscopeMaster()
    mag = mpu.readMagnetometerMaster()
    temperature = mpu.readTemperatureMaster()
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    client.publish('satellite/tumakitu', 'gps')
    
'''

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("Satellite/ImageTaken")
    client.subscribe('satellite/gps')



def transmitdata():
    try:
        count = 0
        file = '/home/pi/Documents/code/images.jpg'
        image = open(file, 'rb')
        image_read = image.read()
        image_64_encode = pybase64.encodebytes(image_read) #encodestring also

        image_decode_bytes = pybase64.b64decode_as_bytearray(image_64_encode)
        image_list = list(image_decode_bytes)
        print(image_list) 
        i = 0
        lens=32
        for j in range(0,len(image_list),lens):

            payload = image_decode_bytes[i:i+lens]
            nrf.reset_packages_lost()
            nrf.send(payload)
            i+=lens
            
            timeout = False
            
            try:
                nrf.wait_until_sent()
            except TimeoutError:
                timeout = True
                
            if not timeout:
                if nrf.get_packages_lost() == 0:    
                    # Check if an acknowledgement package is available.
                    if nrf.data_ready():
                        # Get payload.
                        payload = nrf.get_payload()
        
                        if len(payload) == 4:
                            # If the payload is 4 bytes, we expect it to be an acknowledgement payload.
                            (next_id, ) = struct.unpack('<I', payload)

                        else:
                            # Not 4 bytes long then we consider it an invalid payload.
                            print("Invalid acknowledgement payload received.")
                            next_id = -1
                    else:
                        print("No acknowledgement package received.")
                        next_id = -1

                else:
                    # The package sent was lost.
                    print("Package lost. No acknowledgement.")
                    next_id = -1
            else:
                print("Timeout. No acknowledgement.")
                next_id = -1


            if timeout:
                print(f'Error: timeout while waiting for acknowledgement package. next_id={next_id}')
            
            
            else:
                if nrf.get_packages_lost() == 0:
                    print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
                    print(len(image_list))
                else:
                    print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")

            # Wait 10 seconds before sending the next reading.
            time.sleep(0.2)
    except:
        traceback.print_exc()
        nrf.power_down()
        pi.stop()
        
def on_message(client, userdata, msg):
    topic = msg.topic
    if topic == "Satellite/ImageTaken":
        #collectdata()
        transmitdata()
    elif topic == 'satellite/gps':
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        m_in = json.loads(m_decode)
        latitude = m_in['latitude']
        longitude = m_in['longitude']
        altitude= m_in['altitude']
        speed= m_in['ground_speed']
        heading_status= m_in['imu_alignment_status']
        numSV= m_in['numSV']
    

client = mqtt.Client()
client.connect("localhost", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message
client.publish ("Satellite/camera", "Take photo")
    






import paho.mqtt.client as mqtt
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import Adafruit_ADS1x15  # Import the ADS1x15 module.
import time
# from ubloxm8u import *
import os
import pybase64

latitude, longitude, altitude, speed, inputVoltage, temperature = 0, 0, 0, 0, 0, 0
accel = []
gyro = []
mag = []

import argparse
from datetime import datetime
import struct
import sys
import time
import traceback

import pigpio

from nrf24 import *

mpu = MPU9250(
    address_ak=AK8963_ADDRESS,
    address_mpu_master=MPU9050_ADDRESS_68,  # In 0x68 Address
    address_mpu_slave=None,
    bus=1,
    gfs=GFS_1000,
    afs=AFS_8G,
    mfs=AK8963_BIT_16,
    mode=AK8963_MODE_C100HZ)

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 2 / 3


def getimu(imu):
    imu.configure()  # Apply the settings to the registers.
    print("Accelerometer", imu.readAccelerometerMaster())
    print("Gyroscope", imu.readGyroscopeMaster())
    print("Magnetometer", imu.readMagnetometerMaster())
    print("Temperature", imu.readTemperatureMaster())
    print("\n")
    accel = imu.readAccelerometerMaster()
    gyro = imu.readGyroscopeMaster()
    mag = imu.readMagnetometerMaster()
    temperature = imu.readTemperatureMaster()
    return accel[0], accel[1], accel[2], gyro[0], gyro[1], gyro[2], temperature


def getadc(conv):
    values = [0] * 4
    inputVoltage = (conv.read_adc(0, gain=GAIN))
    return inputVoltage


def getimage():
    output = os.system("python3 /home/pi/Documents/code/final/camera.py")
    print(output)


def getgps():
    lon, lat, alt = 0, 0, 0
    return lon, lat, alt


def collectdata():
    getimu(mpu)
    getadc(adc)
    getgps()
    getimage()


def serialisedimage():
    file = 'image.jpg'
    image = open(file, 'rb')
    image_read = image.read()
    image_64_encode = pybase64.encodebytes(image_read)  # encodestring also

    image_decode_bytes = pybase64.b64decode_as_bytearray(image_64_encode)
    image_list = list(image_decode_bytes)
    print(image_list)
    return len(image_list), image_decode_bytes


if __name__ == "__main__":
    print("Python NRF24 Sender with Acknowledgement Payload Example.")

    # Parse command line argument.
    parser = argparse.ArgumentParser(prog="ack-sender.py",
                                     description="Simple NRF24 Sender with Acknowledgement Payload.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost',
                        help="Hostname for the Raspberry running the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888, help="Port number of the pigpio daemon.")
    parser.add_argument('address', type=str, nargs='?', default='1ACKS',
                        help="Address to send to (3 to 5 ASCII characters).")

    args = parser.parse_args()
    hostname = args.hostname
    port = args.port
    address = args.address

    if not (2 < len(address) < 6):
        print(f'Invalid address {address}. Addresses must be 3 to 5 ASCII characters.')
        sys.exit(1)

    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        exit()

    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.ACK, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS,
                pa_level=RF24_PA.MIN)
    nrf.set_address_bytes(len(address))
    nrf.set_retransmission(15, 15)
    nrf.open_writing_pipe(address)
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, "KORIR")
import paho.mqtt.client as mqtt
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
import Adafruit_ADS1x15  # Import the ADS1x15 module.
import time
# from ubloxm8u import *
import os
import pybase64

latitude, longitude, altitude, speed, inputVoltage, temperature = 0, 0, 0, 0, 0, 0
accel = []
gyro = []
mag = []

import argparse
from datetime import datetime
import struct
import sys
import time
import traceback

import pigpio

from nrf24 import *

mpu = MPU9250(
    address_ak=AK8963_ADDRESS,
    address_mpu_master=MPU9050_ADDRESS_68,  # In 0x68 Address
    address_mpu_slave=None,
    bus=1,
    gfs=GFS_1000,
    afs=AFS_8G,
    mfs=AK8963_BIT_16,
    mode=AK8963_MODE_C100HZ)

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 2 / 3


def getimu(imu):
    imu.configure()  # Apply the settings to the registers.
    print("Accelerometer", imu.readAccelerometerMaster())
    print("Gyroscope", imu.readGyroscopeMaster())
    print("Magnetometer", imu.readMagnetometerMaster())
    print("Temperature", imu.readTemperatureMaster())
    print("\n")
    accel = imu.readAccelerometerMaster()
    gyro = imu.readGyroscopeMaster()
    mag = imu.readMagnetometerMaster()
    temperature = imu.readTemperatureMaster()
    return accel[0], accel[1], accel[2], gyro[0], gyro[1], gyro[2], temperature


def getadc(conv):
    values = [0] * 4
    inputVoltage = (conv.read_adc(0, gain=GAIN))
    return inputVoltage


def getimage():
    output = os.system("python3 /home/pi/Documents/code/final/camera.py")
    print(output)


def getgps():
    lon, lat, alt = 0, 0, 0
    return lon, lat, alt


def collectdata():
    getimu(mpu)
    getadc(adc)
    getgps()
    getimage()


def serialisedimage():
    file = 'image.jpg'
    image = open(file, 'rb')
    image_read = image.read()
    image_64_encode = pybase64.encodebytes(image_read)  # encodestring also

    image_decode_bytes = pybase64.b64decode_as_bytearray(image_64_encode)
    image_list = list(image_decode_bytes)
    print(image_list)
    return len(image_list), image_decode_bytes


if __name__ == "__main__":
    print("Python NRF24 Sender with Acknowledgement Payload Example.")

    # Parse command line argument.
    parser = argparse.ArgumentParser(prog="ack-sender.py",
                                     description="Simple NRF24 Sender with Acknowledgement Payload.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost',
                        help="Hostname for the Raspberry running the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888, help="Port number of the pigpio daemon.")
    parser.add_argument('address', type=str, nargs='?', default='1ACKS',
                        help="Address to send to (3 to 5 ASCII characters).")

    args = parser.parse_args()
    hostname = args.hostname
    port = args.port
    address = args.address

    if not (2 < len(address) < 6):
        print(f'Invalid address {address}. Addresses must be 3 to 5 ASCII characters.')
        sys.exit(1)

    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        exit()

    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.ACK, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS,
                pa_level=RF24_PA.MIN)
    nrf.set_address_bytes(len(address))
    nrf.set_retransmission(15, 15)
    nrf.open_writing_pipe(address)
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, "KORIR")

    while True:
        if indexer == 0:
            while nrf.data_ready():
                payload = nrf.get_payload()

                if len(payload) == 4:
                    # If the payload is 4 bytes, we expect it to be an acknowledgement payload.
                    next_id = struct.unpack('<I', payload)
                    if next_id == 0:
                        print("checkpoint on")

                        indexer = 1
        elif indexer == 1:
            getimage()
            lenimage, imgarray = serialisedimage()
            latitude, longitude, altitude = getgps()
            gyrox, gyroy, gyroz, accela, accelb, accelc, tem = getimu(mpu)
            voltage = getadc(adc)
            nrf.open_writing_pipe(address)
            try:
                # Enter a loop sending data to the address specified.
                print(f"Send data to: {address}")

                i = 0
                lens = 32
                # imgidentifier = [0x04]
                for j in range(0, lenimage, lens):

                    payload = imgarray[i:i + lens]
                    nrf.reset_packages_lost()
                    nrf.send(payload)
                    i += lens

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
                                    (next_id,) = struct.unpack('<I', payload)

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
                            print(lenimage)
                        else:
                            print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")

                    # Wait 10 seconds before sending the next reading.
                    time.sleep(0.1)


                payload0 = struct.pack('Bfffffff', 0x01, gyrox, gyroy, gyroz, accela, accelb, accelc, tem)
                nrf.reset_packages_lost()
                nrf.send(payload0)
                i += lens

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
                                (next_id,) = struct.unpack('<I', payload)

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
                        # print(len(image_list))
                    else:
                        print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")

                # Wait 10 seconds before sending the next reading.
                time.sleep(0.1)

                payload1 = struct.pack('Bfffff', 0x02, latitude, longitude, altitude, lenimage, voltage)
                nrf.reset_packages_lost()
                nrf.send(payload1)


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
                                (next_id,) = struct.unpack('<I', payload)

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
                        # print(len(image_list))
                    else:
                        print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")


                # Wait 10 seconds before sending the next reading.
                indexer = 0
                time.sleep(30)


            except:
                traceback.print_exc()
                nrf.power_down()
                pi.stop()


        else:
            print('waiting for start bit')





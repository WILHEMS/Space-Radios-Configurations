import argparse
import struct
import sys
import time
import traceback

import os
import pigpio
from nrf24 import *
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250


#
# A simple NRF24L sender that connects to a PIGPIO instance on a hostname and port, default "localhost" and 8888, and
# starts sending data on the address specified.  Use the companion program "simple-receiver.py" to receive the data
# from it on a different Raspberry Pi.
#
if __name__ == "__main__": 
    # Parse command line argument.
    parser = argparse.ArgumentParser(prog="simple-sender.py", description="Simple NRF24 Sender Example.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost', help="Hostname for the Raspberry running the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888, help="Port number of the pigpio daemon.")
    parser.add_argument('address', type=str, nargs='?', default='1ACKS', help="Address to send to (3 to 5 ASCII characters).")
    
    args = parser.parse_args()
    hostname = args.hostname
    port = args.port
    address = args.address
    
    mpu = MPU9250(
    address_ak=AK8963_ADDRESS, 
    address_mpu_master=MPU9050_ADDRESS_68, # In 0x68 Address
    address_mpu_slave=None, 
    bus=1,
    gfs=GFS_1000, 
    afs=AFS_8G, 
    mfs=AK8963_BIT_16, 
    mode=AK8963_MODE_C100HZ)

    mpu.configure() 

    if not (2 < len(address) < 6):
        print(f'Invalid address {address}. Addresses must be 3 to 5 ASCII characters.')
        sys.exit(1)

    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.LOW)
    nrf.set_address_bytes(len(address))
    nrf.set_retransmission(15, 15)
    nrf.open_writing_pipe(address)
    
    # Display the content of NRF24L01 device registers.
    nrf.show_registers()

    try:
        accelerometer = mpu.readAccelerometerMaster()
        gyroscope = mpu.readGyroscopeMaster()
        magnetometer = mpu.readMagnetometerMaster()
        temperature = mpu.readTemperatureMaster()
        
        
        payload = struct.pack("<ffffffffff", *accelerometer, *gyroscope, *magnetometer, temperature)
        
        # Send the payload to the address specified above.
        nrf.reset_packages_lost()
        nrf.send(payload)
        
        timeout = False
        try:
            nrf.wait_until_sent()
        except TimeoutError:
            print('Timeout waiting for transmission to complete.')
            timeout = True
            # Wait 10 seconds before sending the next reading.
            time.sleep(10)
            
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
            else:
                print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
        
        os.system("python3 /home/pi/Documents/code/space_controller.py")
        # Wait 10 seconds before sending the next reading.
        time.sleep(10)
    except:
        traceback.print_exc()
        nrf.power_down()
        pi.stop()








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
import os

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



try:
    count = 0
    file = 'image.png'
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
        time.sleep(0.1)
    os.system('python3 /home/pi/Documents/code/v8r.py')
except:
    traceback.print_exc()
    nrf.power_down()
    pi.stop()

    

import argparse
from datetime import datetime
from random import normalvariate
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *
#import numpy as np
from PIL import Image
import pybase64


#
# A simple NRF24L sender that connects to a PIGPIO instance on a hostname and port, default "localhost" and 8888, and
# starts sending data on the address specified.  Use the companion program "simple-receiver.py" to receive the data
# from it on a different Raspberry Pi.
#
if __name__ == "__main__":    
    print("Python NRF24 Simple Sender Example.")
    
    # Parse command line argument.
    parser = argparse.ArgumentParser(prog="v5.py", description="Simple NRF24 Sender Example.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost', help="Hostname for the Raspberry running the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888, help="Port number of the pigpio daemon.")
    parser.add_argument('address', type=str, nargs='?', default='1SNSR', help="Address to send to (3 to 5 ASCII characters).")
    
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
        sys.exit()

    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.LOW)
    nrf.set_address_bytes(len(address))
    nrf.open_writing_pipe(address)
    
    # Display the content of NRF24L01 device registers.
    nrf.show_registers()

    try:
        print(f'Send to {address}')
        count = 0
        while True:
            img_data = '/home/pi/Documents/code/image.jpg' 
            image_encode_bytes = pybase64.encodebytes(open(img_data, "rb").read())
            len_image_encode = len(image_encode_bytes)
            print("The length of encoded bytes", len_image_encode)
            
            image_decode_bytes = pybase64.b64decode_as_bytearray(image_encode_bytes)
            
            image_decode_list = list(image_decode_bytes)
            
            len_list = len(image_decode_list)
            
            # len_list // 2
            divider = 60
            
            #code to send first payload
            payload = struct.pack('<Bi',0x01, len_list)
            print("Length of first payload",len(payload))
            print("sent first payload")
            
            print(divider)
            
            # get the space_range
            if len_list % 60 == 0:
                space_range = len_list // 60
                
            else:
                space_range = len_list // 60
                rem_payload_size = len_list - space_range
            
            #send the payloads
            i = 0
            k=0
            j=60
            for i in range(space_range):
                image_decode_list1 = image_decode_list[k:j]
                
                format_space = 'B' * divider
                
                payload = struct.pack(format_space, *image_decode_list1)
                
                print("sent second payload")
                print(payload)
                print(count)
                nrf.reset_packages_lost()
                nrf.send(payload)
                
                try:
                    nrf.wait_until_sent()
                except TimeoutError:
                    print('Timeout waiting for transmission to complete.')
                    # Wait 10 seconds before sending the next reading.
                    time.sleep(10)
                    continue
                
                if nrf.get_packages_lost() == 0:
                    print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
                else:
                    print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")

                # Wait 10 seconds before sending the next reading.
                k += 60
                j += 60
                time.sleep(0.01)
                count += 1
                
            #last loop
                
            image_decode_list1 = image_decode_list[-rem_payload_size:]
            print("image decode list 1")
            print(image_decode_list1)
                
            format_space = 'B' * rem_payload_size
            
            payload = struct.pack(format_space, *image_decode_list1)
            count += 1
            print("THis is the last payload")
            #print(payload)
            print("sent last payload")
            print(count)
            
            nrf.reset_packages_lost()
            nrf.send(payload)
            payload._clearcache()
            try:
                nrf.wait_until_sent()
            except TimeoutError:
                print('Timeout waiting for transmission to complete.')
                # Wait 10 seconds before sending the next reading.
                time.sleep(10)
                continue
            
            if nrf.get_packages_lost() == 0:
                print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
            else:
                print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
            sys.exit(0)
            time.sleep(100)
            
    except:
        traceback.print_exc()
        nrf.power_down()
        pi.stop()







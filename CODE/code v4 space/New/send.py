import argparse
from datetime import datetime
from random import normalvariate
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *
import pybase64
import sys

hostname = "localhost"
port = 8888
address = '1SNSR'

pi = pigpio.pi(hostname, port)
if not pi.connected:
    print("Not connected to Raspberry Pi ... goodbye.")
    sys.exit()

nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_1MBPS, pa_level=RF24_PA.MAX)
nrf.set_address_bytes(len(address))
nrf.open_writing_pipe(address)
nrf.show_registers()



try:
    count = 0
    file = 'image.jpg'
    image = open(file, 'rb')
    image_read = image.read()
    image_64_encode = pybase64.encodebytes(image_read) #encodestring also works aswell as decodestring

    print(image_64_encode)


    string_to_iterate = image_64_encode
    num = 0
    it =  30

    while num < len(string_to_iterate):
        string_to_send = string_to_iterate[num: num + it: 1]
        num += it
        print(string_to_send)
        print(sys.getsizeof(string_to_send))

        #payload = struct.pack("<Bs", 0x01, string_to_send)
        nrf.reset_packages_lost()
        nrf.send(string_to_send)

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
        time.sleep(0.190)
except:
    traceback.print_exc()
    nrf.power_down()
    pi.stop()


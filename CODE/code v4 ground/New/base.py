from datetime import datetime
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *
import pybase64


hostname = "localhost"
port = 8888
address = '1SNSR'

pi = pigpio.pi(hostname, port)
if not pi.connected:
    print("Not connected to Raspberry Pi ... goodbye.")
    sys.exit()

nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_1MBPS, pa_level=RF24_PA.MAX)
nrf.set_address_bytes(len(address))


# Listen on the address specified as parameter
nrf.open_reading_pipe(RF24_RX_ADDR.P1, address)

# Display the content of NRF24L01 device registers.
nrf.show_registers()

try:
    count = 0
    streams = []
    while True:

        while nrf.data_ready():
            # Count message and record time of reception.
            count += 1
            now = datetime.now()

            # Read pipe and payload for message.
            pipe = nrf.data_pipe()
            payload = nrf.get_payload()

            # Resolve protocol number.
            protocol = payload[0] if len(payload) > 0 else -1

            #hex = ':'.join(f'{i:02x}' for i in payload)

            # Show message received as hex.
            #print(f"{now:%Y-%m-%d %H:%M:%S.%f}: pipe: {pipe}, len: {len(payload)}, bytes: {hex}, count: {count}")

            # If the length of the message is 9 bytes and the first byte is 0x01, then we try to interpret the bytes
            # sent as an example message holding a temperature and humidity sent from the "simple-sender.py" program.

            if payload:
                streams.append(payload)
                print(f" pipe: {pipe}, len: {len(payload)}")
               #values = struct.unpack("<Bs", payload)
                #streams.append(values[1])
               # print(values[1])
               # print(values[0])

                # print(f'Protocol: {values[0]}, temperature: {values[1]}, humidity: {values[2]}')
               # image_64_decode = pybase64.b64decode_as_bytearray(values[1])
                #image_result = open('deer_decode.jpg', 'wb') # create a writable image and write the decoding result
               # image_result.write(image_64_decode)
            elif payload[0] == 0x02:

                values = struct.unpack("<Bs", payload)
                streams.append(values[0])
                print(streams)
                # print(f'Protocol: {values[0]}, temperature: {values[1]}, humidity: {values[2]}')
except:
    traceback.print_exc()
    nrf.power_down()
    pi.stop()


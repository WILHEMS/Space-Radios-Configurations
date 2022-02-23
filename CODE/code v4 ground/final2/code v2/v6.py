from datetime import datetime
import struct
import sys
import time
import traceback
from uuid import uuid4

import pigpio
from nrf24 import *
import pybase64

hostname = "localhost"
port = 8888
address = '1ACKS'

pi = pigpio.pi(hostname, port)
if not pi.connected:
    print("Not connected to Raspberry Pi ... goodbye.")
    sys.exit()

nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_1MBPS,
            pa_level=RF24_PA.MAX)
nrf.set_address_bytes(len(address))

# Listen on the address specified as parameter
nrf.open_reading_pipe(RF24_RX_ADDR.P1, address)

# Display the content of NRF24L01 device registers.
nrf.show_registers()

# Set the UUID that will be the payload of the next acknowledgement.
next_id = 1
nrf.ack_payload(RF24_RX_ADDR.P1, struct.pack('<I', next_id))

try:
    count = 0
    streams = bytearray()
    
    while True:

        while nrf.data_ready():
            # Count message and record time of reception.
            count += 1
            now = datetime.now()

            # Read pipe and payload for message.
            pipe = nrf.data_pipe()
            payload = nrf.get_payload()

            # Resolve protocol number.
            #protocol = payload[0] if len(payload) > 0 else -1

            hex = ':'.join(f'{i:02x}' for i in payload)

            # Show message received as hex.
            print(f"{now:%Y-%m-%d %H:%M:%S.%f}: pipe: {pipe}, len: {len(payload)}, bytes: {hex}, count: {count}")

            # If the length of the message is 9 bytes and the first byte is 0x01, then we try to interpret the bytes
            # sent as an example message holding a temperature and humidity sent from the "simple-sender.py" program.
            
            if payload:
                print(payload)
                print(type(payload))
                #values = struct.unpack("<Bs", payload)
                streams = streams + payload
                
                image_result = open('ground.jpg', 'wb')
                image_result.write(streams)
                
                next_id += 1
                nrf.ack_payload(RF24_RX_ADDR.P1, struct.pack('<I', next_id))
#               print(streams)
    
    ''''
    image_base = bytearray(streams)
    
    image_result = open('ground.jpg', 'wb')
    image_result.write(image_base)
    '''
except:
    print('An error occured')
    traceback.print_exc()
    nrf.power_down()
    pi.stop()




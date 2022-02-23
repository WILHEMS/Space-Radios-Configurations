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
sendaddress = '1ACKS'
recvaddress = 'MUNAS'

pi = pigpio.pi(hostname, port)
if not pi.connected:
    print("Not connected to Raspberry Pi ... goodbye.")
    sys.exit()

nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS,
            pa_level=RF24_PA.MAX)
nrf.set_address_bytes(len(sendaddress))
nrf.set_retransmission(15, 15)

# Listen on the address specified as parameter
nrf.open_reading_pipe(RF24_RX_ADDR.P1, sendaddress)
nrf.open_writing_pipe(recvaddress)
next_id = 0
nrf.ack_payload(RF24_RX_ADDR.P1, struct.pack('<I', next_id))
count = 0
streams = bytearray()


while True:

    try:
        while next_id <= 0:
            payload = struct.pack("<B", 0x01)

            nrf.reset_packages_lost()
            nrf.send(payload) # Send the start payload to the recvaddress specified above.

            # check for timeout
            ########################################################################################################
            timeout = False
            try:
                nrf.wait_until_sent()


            except TimeoutError:
                timeout = True
                print("The boy timed out")

            if not timeout:
                while nrf.get_packages_lost() == 0:
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
                        print("Waiting for ready to transmit")
                        next_id = -1

                else:
                    # The package sent was lost.
                    print("Package lost. Cant establish communication.")
                    next_id = -1
            else:
                print("Timeout. Cant get any response")
                next_id = -1


            if timeout:
                print(f'Error: timeout while waiting for acknowledgement package. next_id={next_id}')
            else:
                if nrf.get_packages_lost() == 0:
                    # The package we sent was successfully received by the server.
                    print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}, next_id={next_id}")
                else:
                    print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}, next_id={next_id}")

        nrf.open_reading_pipe(RF24_RX_ADDR.P1, sendaddress)

        ########################################################################################################

        #####start receiving payload
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

            if len(payload) == 21 and payload[0] == 0x02:
                values = struct.unpack("<Bfffff", payload)

                latitude, longitude, altitude, lenimage, voltage = values[1], values[2], values[3], values[4], \
                                                                   values[5]
                print('Payload two reached successfully')
                print("All data received successfully")
                print("Uploading to database")

                # Set uuid that will be part of the next acknowledgement.
                next_id = -1


                nrf.open_writing_pipe(recvaddress)

                nrf.send(struct.pack('<I', next_id))
                time.sleep(10)
                next_id = 1
                nrf.send(struct.pack('<I', next_id))


                count = 0
                streams = bytearray()


            elif len(payload) == 29 and payload[0] == 0x03:
                values = struct.unpack("<Bfffff", payload)
                gyrox, gyroy, gyroz, accela, accelb, accelc, tem = values[1], values[2], values[3], values[4], \
                                                                   values[5], values[6], values[7]
                print('Payload one reached successfully')
                # Set uuid that will be part of the next acknowledgement.
                next_id += 1
                # nrf.ack_payload(RF24_RX_ADDR.P1, struct.pack('<I', next_id))
            else:
                print(payload)
                print('Image payload received')
                print(type(payload))
                # values = struct.unpack("<Bs", payload)
                if len(payload) == 32:
                    streams = streams + payload
                else:
                    streams = streams + payload
                image_result = open('ground.png', 'wb')
                image_result.write(streams)
                next_id += 1
                # nrf.ack_payload(RF24_RX_ADDR.P1, struct.pack('<I', next_id))


                ####end payload receive
    except:
        print('An error occured')
        traceback.print_exc()
        nrf.power_down()
        pi.stop()



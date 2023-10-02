import socket
import datetime
import logger
import time
import signal
import subprocess
import pandas as pd
import numpy as np
from threading import Thread, get_ident
from messageprocessing import process_message

COLLECT_MEASUREMENTS = False
BUFFER_SIZE=8192
MEASUREMENT_FOLDER = '~/measurements'
buffers = dict()
ingress_addresses = list()
measurements = list()
logger = logger.get_logger()

def decode_buffer(buffer, collected):
    if not collected:
        return buffer.decode('utf-8')
    datas = buffer.decode('utf-8').strip().split(',')
    if len(datas) != 9:
        return {}
    elif ":" in datas[0]:
        data_dict = {
            'timestamp': int(datetime.datetime.now().timestamp() * 1000),
            'boot_timestamp': int(datas[8]),
            'anchor_id': datas[6].strip('"'),
            'tag_id': datas[0].split(':')[1],
            'rssi_pol1': int(datas[1]),
            'angle_azimuth': int(datas[2]),
            'rssi_pol2': int(datas[4]),
            'angle_elevation': int(datas[3]),
            'channel': int(datas[5]),
            # 'user_defined_str': datas[7].strip('"'),
        }
    else:
        data_dict = {
            'timestamp': int(datetime.datetime.now().timestamp() * 1000),
            'boot_timestamp': int(datas[8]),
            'anchor_id': datas[6].strip('"'),
            'tag_id': datas[0],
            'rssi_pol1': int(datas[1]),
            'angle_azimuth': int(datas[2]),
            'rssi_pol2': int(datas[4]),
            'angle_elevation': int(datas[3]),
            'channel': int(datas[5]),
            # 'user_defined_str': datas[7].strip('"'),
        }
    return data_dict


def save_measurments(measurements):
    filename = f'{MEASUREMENT_FOLDER}/m_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
    pd.DataFrame(measurements).to_csv(filename, index=False)

def start_ingress_udp_server(INGRESS_SERVER_IP = '10.42.0.1', INGRESS_SERVER_PORT = 9901):

    server_address = (INGRESS_SERVER_IP, INGRESS_SERVER_PORT)

    # Create a UDP socket and bind the socket to the server address
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(server_address)
    logger.info(f"Ingress UDP server listening on {server_address[0]}:{server_address[1]}")

    last_message_timestamp = datetime.datetime.now().timestamp()
    def start_fallback_timer():
        global last_message_timestamp
        while True:
            logger.info("Checking fallback timer")
            current_time = datetime.datetime.now().timestamp()
            if current_time - last_message_timestamp > 2:
                logger.warning("Last message was over two seconds ago. Quitting.")
                subprocess.run(["pkill", "-f", "init.py"])
            buffers = dict()
            time.sleep(3)
    
    def recieveve_udp_messages():
        Thread(target=start_fallback_timer).start()
        try:
            while True:
                new_buffer, addr = udp_socket.recvfrom(BUFFER_SIZE)

                if addr[0] not in ingress_addresses:
                    ingress_addresses.append(addr[0])
                if addr not in buffers:
                    buffers[addr] = new_buffer
                else:
                    buffers[addr] += new_buffer

                if buffers[addr].startswith(b'\r\n+UUDF:') and buffers[addr].endswith(
                        b'\r\n'):
                    datas = decode_buffer(buffers.pop(addr, None), False)
                    last_message_timestamp = datetime.datetime.now().timestamp()
                    # If we collect the measurements, it's appended to a list
                    if COLLECT_MEASUREMENTS:
                        measurements.append(str(datas))
                    # Else we send it out to the connected hosts
                    else:
                        # Use threading so sending out UDP messages doesn't hold up the main thread
                        processing_thread = Thread(target=process_message, args=(str(datas), ingress_addresses), daemon=True)
                        processing_thread.start()

        except KeyboardInterrupt:
            logger.info("Ingress UDP server stopped.")
            udp_socket.close()
        finally:
            if COLLECT_MEASUREMENTS:
                save_measurments(measurements)
            udp_socket.close()

    Thread(target=recieveve_udp_messages).start()

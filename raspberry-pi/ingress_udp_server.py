import socket
import datetime
import logger
import constants
import time
import threading
import pandas as pd
import numpy as np
from messageprocessing import process_message

COLLECT_MEASUREMENTS = False
buffers = dict()
ingress_addresses = list()
buffered_addresses = list()
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
    filename = f'{constants.MEASUREMENT_FOLDER}/m_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
    pd.DataFrame(measurements).to_csv(filename, index=False)

def start_ingress_udp_server():
    global ingress_addresses, buffered_addresses, buffers, measurements
    server_address = (constants.GATEWAY_IP, constants.INGRESS_SERVER_PORT)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(server_address)
    logger.info(f"Ingress UDP server listening on {server_address[0]}:{server_address[1]}")
    
    try:
        while True:
            data, addr = get_current_udp_message(udp_socket, constants.BUFFER_SIZE)
            if COLLECT_MEASUREMENTS:
                if addr[0] not in ingress_addresses:
                    ingress_addresses.append(addr[0])
                if addr not in buffers:
                    buffers[addr] = data
                else:
                    buffers[addr] += data
                if buffers[addr].startswith(b'\r\n+UUDF:') and buffers[addr].endswith(
                        b'\r\n'):
                    datas = decode_buffer(buffers.pop(addr, None), False)
                    # If we collect the measurements, it's appended to a list
                    if COLLECT_MEASUREMENTS:
                        measurements.append(str(datas))

            else:
                if addr[0] not in ingress_addresses:
                    ingress_addresses.append(addr[0])
                if addr[0] not in buffered_addresses:
                    buffered_addresses.append(addr[0])
                if addr not in buffers:
                    buffers[addr] = data

                if len(buffers) == len(ingress_addresses):
                    datas = list()
                    for addr, buffer_value in buffers.items():
                        logger.info(str(buffer_value))
                        if buffer_value.startswith(b'\r\n+UUDF:') and buffer_value.endswith(
                                b'\r\n'):
                            datas.append(decode_buffer(buffer_value, True))

                    threading.Thread(target=process_message, args=[datas]).start()
                    ingress_addresses = buffered_addresses
                    buffered_addresses = list()
                    buffers = dict()
                    logger.info("sleeping")
                    time.sleep(0.9)
    except KeyboardInterrupt:
        logger.info("Ingress UDP server stopped.")
        udp_socket.close()
    finally:
        if COLLECT_MEASUREMENTS:
            save_measurments(measurements)
        udp_socket.close()

def get_current_udp_message(udp_socket, buffer_size):
    udp_socket.setblocking(0)

    while True:
        try:
            data, addr = udp_socket.recvfrom(buffer_size)
        except socket.error:
            break

    udp_socket.setblocking(1)
    data, addr = udp_socket.recvfrom(buffer_size)
    return data, addr

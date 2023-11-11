import socket
import datetime
import logger
import constants
import time
import threading
import pandas as pd
import numpy as np
import positioning
import os
import shutil
from messageprocessing import process_message

buffers = dict()
ingress_addresses = list()
measurements = list()
logger = logger.get_logger()

def save_on_exit():
    if constants.COLLECT_MEASUREMENTS:
        save_measurments(measurements)

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

def get_tag_id_from_buffer(buffer):
    datas = buffer.decode('utf-8').strip().split(',')
    ret = ""
    if len(datas) != 9:
        ret = {}
    elif ":" in datas[0]:
        ret = datas[0].split(':')[1]
    else:
        ret = datas[0]

    return str(ret)

def save_measurments(measurements):
    OUTPUT_FOLDER = os.path.join(constants.MEASUREMENT_FOLDER, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    OUTPUT_CONFIG_FOLDER = os.path.join(OUTPUT_FOLDER, "config")
    os.makedirs(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_CONFIG_FOLDER)
    logger.info("Saving measurements to %s", str(OUTPUT_FOLDER))
    files = os.listdir(constants.CONFIG_FOLDER)
    for file in files:
        shutil.copy2(os.path.join(constants.CONFIG_FOLDER,file), OUTPUT_CONFIG_FOLDER)

    for tag_id in set(measurement['tag_id'] for measurement in measurements):
        filtered_measurements = [measurement for measurement in measurements if measurement['tag_id'] == tag_id]
        measurements_df = pd.DataFrame(filtered_measurements)
        csv_file_path = os.path.join(OUTPUT_FOLDER, f"{tag_id}_measurements.csv")
        measurements_df.to_csv(csv_file_path, index=False)

def start_ingress_udp_server():
    global ingress_addresses, buffers, measurements
    server_address = (constants.GATEWAY_IP, constants.INGRESS_SERVER_PORT)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(server_address)
    logger.info(f"Ingress UDP server listening on {server_address[0]}:{server_address[1]}")
    current_buffer = dict()
    
    try:
        while True:
            data, addr = get_current_udp_message(udp_socket, constants.BUFFER_SIZE)

            if addr[0] not in ingress_addresses:
                ingress_addresses.append(addr[0])

            if constants.COLLECT_MEASUREMENTS:
                if addr not in buffers:
                    buffers[addr] = data
                else:
                    buffers[addr] += data
                if buffers[addr].startswith(b'\r\n+UUDF:') and buffers[addr].endswith(
                        b'\r\n'):
                    datas = decode_buffer(buffers.pop(addr, None), True)
                    measurements.append(datas)

            else:
                tag_id = get_tag_id_from_buffer(data)
                if tag_id not in buffers:
                    buffers[tag_id] = dict()
                buffers[tag_id][addr[0]] = data
                if tag_id not in current_buffer:
                    current_buffer[tag_id] = 1
                else:
                    current_buffer[tag_id] += 1
                
                reached_max_size = False
                for tag_id, buffer_size_with_tag_id in current_buffer.items():
                    if buffer_size_with_tag_id == constants.MAX_BUFFER_SIZE:
                        reached_max_size = True

                if reached_max_size:
                    datas = dict()
                    for tag_id, buffer_with_addr in buffers.items():
                        datas[tag_id] = list()
                        for addr, buffer_value in buffer_with_addr.items():
                            logger.info(str(buffer_value))
                            if buffer_value.startswith(b'\r\n+UUDF:') and buffer_value.endswith(
                                    b'\r\n'):
                                datas[tag_id].append(decode_buffer(buffer_value, True))
                    threading.Thread(target=process_message, args=[datas]).start()
                    buffers = dict()
                    current_buffer = dict()
                    udp_socket.setblocking(1)
                    logger.info("sleeping")
                    time.sleep(0.9)
    except KeyboardInterrupt:
        logger.info("Ingress UDP server stopped.")
        udp_socket.close()
    finally:
        if constants.COLLECT_MEASUREMENTS:
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

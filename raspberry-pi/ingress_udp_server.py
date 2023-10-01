import socket
import datetime
import pandas as pd
import numpy as np
from messageprocessing import process_message

COLLECT_MEASUREMENTS = True
BUFFER_SIZE=8192
MEASUREMENT_FOLDER = '~/measurements'
buffers = dict()
measurements = list()

def decode_buffer(buffer):
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
    print(data_dict)
    return data_dict


def save_measurments(measurements):
    filename = f'{MEASUREMENT_FOLDER}/m_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
    pd.DataFrame(measurements).to_csv(filename, index=False)

def start_ingress_udp_server(INGRESS_SERVER_IP = '10.42.0.1', INGRESS_SERVER_PORT = 9901):
    
    server_address = (INGRESS_SERVER_IP, INGRESS_SERVER_PORT)

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the server address
    udp_socket.bind(server_address)
    
    print(f"Ingress UDP server listening on {server_address[0]}:{server_address[1]}")

    try:
        while True:
            new_buffer, addr = udp_socket.recvfrom(BUFFER_SIZE)

            if addr not in buffers:
                buffers[addr] = new_buffer
            else:
                buffers[addr] += new_buffer

            if buffers[addr].startswith(b'\r\n+UUDF:') and buffers[addr].endswith(
                    b'\r\n'):
                datas = decode_buffer(buffers.pop(addr, None))
            if COLLECT_MEASUREMENTS and datas:
                measurements.append(datas)
            else:
                process_message(datas)

    except KeyboardInterrupt:
        print("Ingress UDP server stopped.")
    finally:
        if COLLECT_MEASUREMENTS:
            save_measurments(measurements)
        udp_socket.close()

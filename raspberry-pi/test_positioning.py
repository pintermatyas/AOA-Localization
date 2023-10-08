# Standard library imports.
import glob

# Related third party imports.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import socket
import constants

# Local application/library specific imports.
import processing as processing
import positioning
from scapy.all import *
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import send

def test_positioning_functionality():
    time_before = datetime.datetime.now().timestamp()
    print(time_before)
    filename = '22-02-22-p-a12'
    df = pd.read_csv('./test-data/test_position.csv')
    df = df.query("`tag_id`=='6C1DEBA4241B'")
    # df = pd.concat([pd.read_csv(file) for file in sorted(glob.glob(PROCESSED+'p_*'))]).reset_index(drop=True)

    anchors = pd.read_csv('test-data/anchors.csv')
    anchors = anchors.set_index(anchors['anchor_id'])
    anchors.index.name = 'id'

    processing.add_true_angle(df, anchors)

    df['angle_azimuth_diff'] = df['angle_azimuth_true'] - df['angle_azimuth']
    bps = positioning.BluetoothPositionSystem()
    est_pos = bps.aoa_2(df, anchors)
    print(datetime.datetime.now().timestamp() - time_before)
    print(est_pos['est_pos'])


def send_spoofed_packet(src_ip, dst_ip, src_port, dst_port, payload):
    ip = IP(src=src_ip, dst=dst_ip)
    udp = UDP(sport=src_port, dport=dst_port)
    packet = ip/udp/payload
    send(packet)

def test_real_life_scenario():
    first = "\r\n+UUDF:6C1DEBA4241B,-65,26,-65,6,37,\"CCF9579B21AE\",\"\",1129320\r\n"
    second = "\r\n+UUDF:6C1DEBA4241B,-59,32,-67,0,39,\"CCF9579B217F\",\"\",1117130\r\n"
    third = "\r\n+UUDF:6C1DEBA4241B,-62,38,-58,8,39,\"CCF9579B22B0\",\"\",1111242\r\n"

    server_address = (constants.GATEWAY_IP, constants.INGRESS_SERVER_PORT)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        #udp_socket.sendto(first.encode('utf-8'), server_address)
        send_spoofed_packet("1.2.3.4", constants.GATEWAY_IP, 12345, constants.INGRESS_SERVER_PORT, first)
        #udp_socket.sendto(second.encode('utf-8'), server_address)
        send_spoofed_packet("1.2.3.5", constants.GATEWAY_IP, 12345, constants.INGRESS_SERVER_PORT, second)
        #udp_socket.sendto(third.encode('utf-8'), server_address)
        send_spoofed_packet("1.2.3.6", constants.GATEWAY_IP, 12345, constants.INGRESS_SERVER_PORT, third)
        print("sent to " + str(server_address))

test_real_life_scenario()
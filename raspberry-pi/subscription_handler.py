import socket
import logger
import constants
from threading import Thread

logger = logger.get_logger()
subscribed_devices = list()

def start_subscription_handler():
    server_address = (constants.GATEWAY_IP, constants.SUBSCRIPTION_PORT)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(server_address)
    logger.info(f"Subscription handler listening on {server_address[0]}:{server_address[1]}")
    while True:
        buffer, addr = udp_socket.recvfrom(constants.BUFFER_SIZE)
        data = buffer.decode('utf-8')
        if ("Subscribe" in data) and (addr[0] not in subscribed_devices):
            subscribed_devices.append(addr[0])
            logger.info(str(addr[0]) + " subscribed!")
        elif ("Unsubscribe" in data) and (addr[0] in subscribed_devices):
            subscribed_devices.remove(addr[0])
            logger.info(str(addr[0]) + " unsubscribed!")
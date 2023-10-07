import socket
import subscription_handler
import logger
import constants

logger = logger.get_logger()

def multicast_udp_message(message):

    ip_addresses = subscription_handler.subscribed_devices
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ipaddr in ip_addresses:
        try:
            server_address = (str(ipaddr), constants.EGRESS_PORT)
            # Send the message to the server
            udp_socket.sendto(str(message).encode('utf-8'), server_address)
        except KeyboardInterrupt:
            logger.warning("Output UDP socket has been interrupted, quitting.")
            pass

    if len(ip_addresses) == 0:
        logger.info("No subscribed devices!")
    else:
        logger.info("Multicasted UDP message " + str(message) + " to " + str(ip_addresses))
    udp_socket.close()
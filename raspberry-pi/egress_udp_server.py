import socket
import hosts
import logger

logger = logger.get_logger()

def multicast_udp_message(message, ingress_addresses, egress_server_port):

    ip_addresses = hosts.get_connected_hosts()
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    egress_addresses = list()

    for ipaddr in ip_addresses:
        if str(ipaddr) not in ingress_addresses:
            try:
                server_address = (str(ipaddr), egress_server_port)
                # Send the message to the server
                udp_socket.sendto(message.encode('utf-8'), server_address)
                egress_addresses.append(str(ipaddr))
            except KeyboardInterrupt:
                logger.warning("Output UDP socket has been interrupted, quitting.")
                pass

    logger.info("Multicasted UDP message " + message + " to " + str(egress_addresses))
    udp_socket.close()
import socket
import hosts

def multicast_udp_message(message, ingress_addresses, egress_server_port):

    ip_addresses = hosts.get_connected_hosts()
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ipaddr in ip_addresses:
        if str(ipaddr) not in ingress_addresses:
            try:
                server_address = (str(ipaddr), egress_server_port)
                # Send the message to the server
                udp_socket.sendto(message.encode('utf-8'), server_address)
                print("sent UDP message " + message + " to " + str(ipaddr))
            except KeyboardInterrupt:
                pass

    udp_socket.close()
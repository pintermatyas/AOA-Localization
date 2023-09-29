import socket

def send_udp_message(message, EGRESS_SERVER_IP = '10.42.0.1', EGRESS_SERVER_PORT = 9902):
    
    server_address = (EGRESS_SERVER_IP, EGRESS_SERVER_PORT)

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
       
       # Send the message to the server
       udp_socket.sendto(message.encode('utf-8'), server_address)

    except KeyboardInterrupt:
        pass
    finally:
        udp_socket.close()
from egress_udp_server import send_udp_message

EGRESS_SERVER_IP = '10.42.0.1'
EGRESS_SERVER_PORT = 9902

def process_message(message):
    send_udp_message(message, EGRESS_SERVER_IP, EGRESS_SERVER_PORT)

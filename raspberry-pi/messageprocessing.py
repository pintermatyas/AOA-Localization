from egress_udp_server import send_udp_message

EGRESS_SERVER_IP = '10.42.0.99' # Static IP of my connected phone
EGRESS_SERVER_PORT = 9902

def process_message(message):
    #print("processing message %s", str(message))
    send_udp_message(message, EGRESS_SERVER_IP, EGRESS_SERVER_PORT)

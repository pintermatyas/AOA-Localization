from egress_udp_server import multicast_udp_message

egress_server_port = 9902

def process_message(message, ingress_addresses):
    # Here comes the positioning logic
    multicast_udp_message(message, ingress_addresses, egress_server_port)

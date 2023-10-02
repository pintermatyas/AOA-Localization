import logger
import threading
from egress_udp_server import multicast_udp_message

egress_server_port = 9902
logger = logger.get_logger()

def process_message(message, ingress_addresses):
    logger.info("Processing message " + str(message))
    # Here comes the positioning logic

    multicast_udp_message(message, ingress_addresses, egress_server_port)

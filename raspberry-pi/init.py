import ingress_udp_server
import subscription_handler
import constants
import os
import logger
from threading import Thread
logger = logger.get_logger()

if not os.path.exists(constants.MEASUREMENT_FOLDER):
    os.makedirs(constants.MEASUREMENT_FOLDER)
    logger.info("Created measurements folder")
else:
    logger.info("Measurements folder already exists!")

try:
    subscription = Thread(target=subscription_handler.start_subscription_handler, daemon=True)
    ingress_server = Thread(target=ingress_udp_server.start_ingress_udp_server, daemon=True)
    subscription.start()
    ingress_server.start()
    subscription.join()
    ingress_server.join()
except KeyboardInterrupt:
    if constants.COLLECT_MEASUREMENTS:
        logger.error("Got KeyboardInterrupt. Saving measurements on exit.")
        ingress_udp_server.save_on_exit()
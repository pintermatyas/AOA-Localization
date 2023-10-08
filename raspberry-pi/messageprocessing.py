import logger
import threading
import positioning
import processing
import constants
import pandas as pd
from egress_udp_server import multicast_udp_message

logger = logger.get_logger()
anchors = pd.read_csv(constants.CONFIG_FOLDER + '/anchors.csv')
anchors = anchors.set_index(anchors['anchor_id'])

def process_message(message):
    logger.info("Processing message " + str(message))
    df = pd.DataFrame.from_dict(message)
    bps = positioning.BluetoothPositionSystem()
    est_pos = bps.aoa_2(df, anchors)
    multicast_udp_message(est_pos)
import logger
import positioning
import constants
import numpy as np
import pandas as pd
from egress_udp_server import multicast_udp_message

logger = logger.get_logger()

def process_message(message):
    anchors = pd.read_csv(constants.CONFIG_FOLDER + '/anchors.csv')
    anchors = anchors.set_index(anchors['anchor_id'])
    logger.info("Processing message " + str(message))
    df = pd.DataFrame.from_dict(message)
    bps = positioning.BluetoothPositionSystem()
    est_pos = bps.aoa_2(df, anchors)
    avg_pos = np.nanmean(est_pos['est_pos'], axis=0)
    lowest_x = anchors['x'].min()
    highest_x = anchors['x'].max()
    lowest_y = anchors['y'].min()
    highest_y = anchors['y'].max()

    lowest_coordinates = (lowest_x, lowest_y)
    highest_coordinates = (highest_x, highest_y)

    multicast_udp_message(str(avg_pos) + ";" + str(lowest_coordinates) + "," + str(highest_coordinates))
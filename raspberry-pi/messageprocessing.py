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

    coordinate_string = ";".join(anchors.apply(lambda row: f"{row['x']},{row['y']}", axis=1))

    multicast_udp_message(str(avg_pos[0]) + ","+ str(avg_pos[1]) + ";;" + coordinate_string)
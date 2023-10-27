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
    est_pos_list = list()
    for tag_id, measurements in message.items():
        df = pd.DataFrame.from_dict(measurements)
        bps = positioning.BluetoothPositionSystem()
        est_pos = bps.aoa_2(df, anchors)
        if est_pos['est_pos'].size !=  0:
            avg_pos = np.nanmean(est_pos['est_pos'], axis=0)
            if avg_pos[0] == np.nan or avg_pos[1] == np.nan:
                continue
            else:
                est_pos_list.append(avg_pos)
    
    est_pos_string = ""
    if len(est_pos_list) == 1:
        est_pos_string = f"{est_pos_list[0][0]},{est_pos_list[0][1]}"
    else:
        est_pos_string = ";".join([f"{row[0]},{row[1]}" for row in est_pos_list])
    coordinate_string = ";".join(anchors.apply(lambda row: f"{row['x']},{row['y']}", axis=1))

    multicast_udp_message(str(est_pos_string) + ";;" + str(coordinate_string))
# Standard library imports.
import glob

# Related third party imports.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

# Local application/library specific imports.
import processing as processing
import positioning


time_before = datetime.datetime.now().timestamp()
print(time_before)
filename = '22-02-22-p-a12'
df = pd.read_csv('./test-data/test_position.csv')
df = df.query("`tag_id`=='6C1DEBA4241B'")
# df = pd.concat([pd.read_csv(file) for file in sorted(glob.glob(PROCESSED+'p_*'))]).reset_index(drop=True)

anchors = pd.read_csv('test-data/anchors.csv')
anchors = anchors.set_index(anchors['anchor_id'])
anchors.index.name = 'id'

processing.add_true_angle(df, anchors)

df['angle_azimuth_diff'] = df['angle_azimuth_true'] - df['angle_azimuth']
bps = positioning.BluetoothPositionSystem()
est_pos = bps.aoa_2(df, anchors)
print(datetime.datetime.now().timestamp() - time_before)
print(est_pos['est_pos'])
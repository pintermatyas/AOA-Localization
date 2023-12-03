import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

measurement_path = '/home/pi/Downloads/AOA-Localization/raspberry-pi/measurements/'
CCF9579B223C = measurement_path + 'CCF9579B223C_all_measurements.csv'
CCF9579B217F = measurement_path + 'CCF9579B217F_all_measurements.csv'

CCF9579B223C_dataframe = pd.read_csv(CCF9579B223C)['angle_azimuth'].tolist()
CCF9579B217F_dataframe = pd.read_csv(CCF9579B217F)['angle_azimuth'].tolist()

plt.hist(CCF9579B223C_dataframe, 40)
plt.savefig(measurement_path + 'CCF9579B223C_histogram.png')
plt.clf()

plt.hist(CCF9579B217F_dataframe, 40)
plt.savefig(measurement_path + 'CCF9579B217F_histogram.png')
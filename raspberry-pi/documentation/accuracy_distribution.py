import pandas as pd
from pandas import DataFrame as df
import matplotlib.pyplot as plt
import numpy as np

accuracy = pd.read_csv('/home/pi/Downloads/AOA-Localization/raspberry-pi/measurements/accuracy.csv')['accuracy'].values

filtered_accuracy = []

for acc in accuracy:
    if np.isfinite(acc) and acc < 50:
        filtered_accuracy.append(acc)

plt.hist(filtered_accuracy, bins=150)
plt.xlim((0,10))
xticks = np.arange(0, 10.5, 1)
plt.xticks(xticks)
plt.xlabel('Accuracy of positioning')
plt.ylabel('Frequency of measured accuracy')
plt.savefig('/home/pi/Downloads/AOA-Localization/raspberry-pi/documentation/accuracy_distribution.png')
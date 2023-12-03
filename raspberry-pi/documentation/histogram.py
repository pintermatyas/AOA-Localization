import csv
import matplotlib.pyplot as plt
import numpy as np

ylim=5

csv_file_path = "/home/pi/Downloads/AOA-Localization/raspberry-pi/measurements/accuracy.csv"

accuracy_values_of_biggest_azimuth = dict()
azimuth_values = []

with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)
    for row in csv_reader:
        if row[1] not in accuracy_values_of_biggest_azimuth:
            accuracy_values_of_biggest_azimuth[row[1]] = []
        accuracy_values_of_biggest_azimuth[row[1]].append(float(row[0]))

all_data_x = []
all_data_y = []

for key, value in accuracy_values_of_biggest_azimuth.items():
    for accuracy in value:
        if accuracy != 'nan' and accuracy <= ylim:
            all_data_x.append(float(key))
            all_data_y.append(accuracy)
plt.scatter(all_data_x, all_data_y, color='red', marker='o', alpha=0.1)
#Trendline for plot
z = np.polyfit(all_data_x, all_data_y, 1)
p = np.poly1d(z)
plt.plot(all_data_x, p(all_data_x), color='blue')
plt.title('Accuracy vs Biggest Azimuth Angle in the measurement window')
plt.xlabel('Biggest Azimuth Angle in the measurement')
plt.ylabel('Accuracy (meters)')
plt.grid(True)
plt.ylim(0, ylim)
plt.show()
plt.savefig("/home/pi/Downloads/AOA-Localization/raspberry-pi/measurements/accuracy.png")
plt.clf()

keys_float = []
values = []
for key, value in accuracy_values_of_biggest_azimuth.items():
    if np.nanmean(value) <= ylim:
        keys_float.append(float(key))
        values.append(np.nanmean(value))
plt.scatter(keys_float, values, color='blue', marker='o')
#Trendline for plot
z = np.polyfit(keys_float, values, 1)
p = np.poly1d(z)
plt.plot(keys_float, p(keys_float), color='red')
plt.title('Average Accuracy vs Biggest Azimuth Angle in the measurement window')
plt.xlabel('Biggest Azimuth Angle in the measurement')
plt.ylabel('Accuracy (meters)')
plt.grid(True)
plt.show()
plt.ylim(0, ylim)
plt.savefig("/home/pi/Downloads/AOA-Localization/raspberry-pi/measurements/accuracy_avg.png")
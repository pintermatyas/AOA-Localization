import sys
import os
import numpy as np
import math
import pandas as pd
import positioning
import figure_with_angles
import csv
import matplotlib.pyplot as plt

__test_anchor_coordinates = [(1, 1), (2, 3), (3, 2)]
__test_real_position = [(0.5, 1.5), (2.5, 3.5), (3.5, 2.5)]
__test_estimated_position = [(1.2, 1.8), (2.2, 3.2), (3.2, 2.2)]

measurement_folder_path = sys.argv[1]
csv_file_path = "/home/pi/Downloads/AOA-Localization/raspberry-pi/measurements/accuracy.csv"

def get_filenames(measurement_path):
    measurement_path += "/"
    config_file_path = measurement_path + "config/"
    anchor_config_path = config_file_path + "anchors.csv"
    tag_coordinate_path = config_file_path + "tag_coordinates.csv"

    measurement_file = ""
    files = os.listdir(measurement_path)
    for file in files:
        if "measurement" in file:
            measurement_file = measurement_path + file

    return tag_coordinate_path, anchor_config_path, measurement_file

tag_coordinate_path, anchor_config_path, measurement_file = get_filenames(measurement_folder_path)

def create_image(anchor_coordinates, real_coordinate, estimated_positions):
    fig, ax = plt.subplots()
    bbox = [(-0.5, -0.5), (4, 4)]

    ax.scatter(*zip(*estimated_positions), color='red', alpha=0.1, label='Estimated Position')
    ax.scatter(*zip(*anchor_coordinates), color='blue', alpha=1, label='Anchor Coordinates')
    ax.scatter(*zip(*real_coordinate), color='green', alpha=1, label='Real Position')

    ax.set_xlim(bbox[0][0], bbox[1][0])
    ax.set_ylim(bbox[0][1], bbox[1][1])

    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Position Plot')
    ax.legend()

    output_path = os.path.join(measurement_folder_path, 'output.png')
    print(output_path)
    plt.savefig(output_path)

anchors = pd.read_csv(anchor_config_path)
anchors = anchors.set_index(anchors['anchor_id'])
anchor_coordinates = list(zip(anchors['x'], anchors['y']))

real_position_df = pd.read_csv(tag_coordinate_path)
real_position_df = real_position_df.set_index(real_position_df['tag_id'])
real_position = list(zip(real_position_df['x'], real_position_df['y']))

accuracy_analysis = list()


measurements = pd.read_csv(measurement_file).to_dict(orient='records')
windows = []
window_size = 8
for i in range(0, len(measurements), window_size):
    window = measurements[i:i + window_size]
    windows.append(window)

est_pos_list = list()
list_of_pos_dir = list()
for window in windows:
    df = pd.DataFrame.from_dict(window)
    bps = positioning.BluetoothPositionSystem()
    est_pos = bps.aoa_2(df, anchors)
    if est_pos['est_pos'].size !=  0:
        avg_pos = np.nanmean(est_pos['est_pos'], axis=0)
        est_pos_list.append(avg_pos)

    azimuth_angles_list = list()
    biggest_angle = 0
    for anchor_id in set(measurement['anchor_id'] for measurement in window):
        filtered_measurements = [measurement for measurement in window if measurement['anchor_id'] == anchor_id]
        for measurement in filtered_measurements:
            azimuth = measurement['angle_azimuth']
            biggest_angle = np.max([np.abs(azimuth), biggest_angle])
            azimuth_angles_list.append(azimuth)
            angle_anchor = anchors.loc[anchor_id, 'angle_azimuth']
            true_angle = angle_anchor - azimuth
            anchor_position = anchors.loc[anchor_id, ['x', 'y']].to_numpy()
            list_of_pos_dir.append([anchor_position, true_angle])

    accuracy = math.dist(est_pos_list[-1], real_position[0])
    accuracy_analysis.append([accuracy, biggest_angle])

# Open the CSV file in append mode
with open(csv_file_path, 'a', newline='') as csvfile:
    # Create a CSV writer object
    csv_writer = csv.writer(csvfile)
    for element in accuracy_analysis:
    # Append the two lists as a row in the CSV file
        csv_writer.writerow(element)

cleaned_coordinates = [[coord[0], coord[1]] for coord in est_pos_list if not math.isnan(coord[0])]

figure_with_angles.plot_line_from_point_and_direction(list_of_pos_dir, anchor_coordinates, real_position[0], measurement_folder_path)
create_image(anchor_coordinates, real_position, cleaned_coordinates)
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_line_from_point_and_direction(list_of_dirs, anchors, real_position, image_path):
    bbox = [(-0.5, -0.5), (4, 4)]
    plt.xlim(bbox[0][0], bbox[1][0])
    plt.ylim(bbox[0][1], bbox[1][1])

    anchor_x_coordinates, anchor_y_coordinates = zip(*anchors)

    plt.scatter(anchor_x_coordinates, anchor_y_coordinates, marker='s', color='black', label="Anchors")

    for point, direction_angle in list_of_dirs:
        angle_radians = np.radians(direction_angle)
        line_length = 5
        endpoint_x = point[0] + line_length * np.cos(angle_radians)
        endpoint_y = point[1] + line_length * np.sin(angle_radians)
        plt.plot([point[0], endpoint_x], [point[1], endpoint_y], color='red', linewidth=0.5, alpha=0.05)
    
    plt.plot(real_position[0], real_position[1], marker='v', color='green', label="Real position")
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Figure of the direction of the measurements')
    plt.legend()

    # Save the plot
    output_path = os.path.join(image_path, 'angles.png')
    plt.savefig(output_path)
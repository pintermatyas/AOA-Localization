# Standard library imports.

# Related third party imports.
import numpy as np

# Local application/library specific imports.


def add_position_from_timestamp(df, start_position, end_position):
    start_time, end_time = df['timestamp'].min(), df['timestamp'].max()
    elapsed_time = end_time - start_time
    start_position, end_position = np.array(start_position), np.array(
        end_position)
    movement_direction = (end_position - start_position).reshape(
        (1, -1)) * np.ones((len(df), 3))

    print(start_time, end_time)
    print(elapsed_time)
    print(start_position, end_position)
    print(movement_direction[0])

    df[['x', 'y', 'z']] = start_position + movement_direction * (
        (df['timestamp'].to_numpy() - start_time) / elapsed_time).reshape(
            -1, 1)


def adjust_rotation(df, anchors):
    df = df.copy(deep=True)
    for i, anchor_data in anchors.iterrows():
        if anchor_data['angle_rotation'] == 90:
            anchor_id = anchor_data["anchor_id"]
            dfa = df.query('`anchor_id`==@anchor_id')
            df.loc[df['anchor_id'] == anchor_id,
                   'angle_azimuth'] = dfa['angle_elevation']
            df.loc[df['anchor_id'] == anchor_id,
                   'angle_elevation'] = -dfa['angle_azimuth']
            df.loc[df['anchor_id'] == anchor_id,
                   'rssi_pol1'] = dfa['rssi_pol2']
            df.loc[df['anchor_id'] == anchor_id,
                   'rssi_pol2'] = dfa['rssi_pol1']
    return df


def euclidean_distance(X, Y):
    """Returns distance between vector of points"""
    if len(X.shape) == 2 and len(Y.shape) == 2:
        return np.sqrt(np.sum(np.square(X - Y), axis=1))
    else:
        return np.array([np.nan] * len(X))


def mean_euclidean_distance(X, Y):
    return np.nanmean(euclidean_distance(X, Y))


def calculate_angle_error(position, anchor_position, angle, anchor_angle):
    deltaX = position[0] - anchor_position[:, 0]
    deltaY = position[1] - anchor_position[:, 1]
    m2a_angle = np.degrees(np.arctan2(deltaY, deltaX))  # % 360
    # anchor_angle[(anchor_angle == 0) & (m2a_angle > 180)] = 360
    m2a_angle_adj = anchor_angle - m2a_angle
    angle_error = angle - m2a_angle_adj
    return angle_error


def add_true_angle(df, anchors):
    """Calculated true azimuth angle from position"""
    measurement_positions = df[['x', 'y']].to_numpy()
    anchor_positions = anchors.loc[df['anchor_id'], ['x', 'y']].to_numpy()

    m2a_distance = euclidean_distance(measurement_positions, anchor_positions)

    deltaX = measurement_positions[:, 0] - anchor_positions[:, 0]
    deltaY = measurement_positions[:, 1] - anchor_positions[:, 1]
    m2a_angle = np.degrees(np.arctan2(deltaY, deltaX)) % 360
    anchor_angle = anchors.loc[df['anchor_id'],
                               ['angle_azimuth']].to_numpy().ravel()
    anchor_angle[(anchor_angle == 0) & (m2a_angle > 180)] = 360
    m2a_angle_adj = anchor_angle - m2a_angle

    df['m2a_distance'] = m2a_distance
    df['angle_azimuth_true'] = m2a_angle_adj
    return


def log_fit(x, y):
    """Fit logarithmic curve"""
    sumy = np.sum(y)
    sumlogx = np.sum(np.log(x))

    b = (x.size * np.sum(y * np.log(x)) -
         sumy * sumlogx) / (x.size * np.sum(np.log(x)**2) - sumlogx**2)
    a = (sumy - b * sumlogx) / x.size

    return a, b


def filter_nan(array_list: list = None):
    filter_nan = ~np.any([
        np.isnan(array).any(axis=1)
        for array in array_list if len(array.shape) == 2
    ],
                         axis=0)
    # print(f"Total: {filter_nan.shape} Filtered: {np.sum(~filter_nan)}")
    return [array[filter_nan] for array in array_list]


##### BP


def join_anchors(df, anchors):
    anchors = anchors.set_index(anchors['anchor_id'])
    anchors.index.name = 'id'
    df = df.join(anchors, on='anchor_id', rsuffix='_anchor')
    return df


def add_params(df):
    df['vx'] = np.cos(
        np.radians(df['angle_azimuth_anchor'] - df['angle_azimuth']))
    df['vy'] = np.sin(
        np.radians(df['angle_azimuth_anchor'] - df['angle_azimuth']))
    df['parA'] = df['vy']
    df['parB'] = (-1) * df['vx']
    df['parC'] = (-1) * df['x_anchor'] * df['vy'] + df['y_anchor'] * df['vx']
    return


def add_true_params(df):
    df['vx_true'] = np.cos(
        np.radians(df['angle_azimuth_anchor'] - df['angle_azimuth_true']))
    df['vy_true'] = np.sin(
        np.radians(df['angle_azimuth_anchor'] - df['angle_azimuth_true']))
    df['parA_true'] = df['vy_true']
    df['parB_true'] = (-1) * df['vx_true']
    df['parC_true'] = (
        -1) * df['x_anchor'] * df['vy_true'] + df['y_anchor'] * df['vx_true']
    return
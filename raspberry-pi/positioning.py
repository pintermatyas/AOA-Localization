# Standard library imports.
import collections
import math

# Related third party imports.
import numpy as np

# Local application/library specific imports.
import filtering as filtering
import processing as processing


class BluetoothPositionSystem:
    def __init__(self) -> None:
        pass

    def localize(self,
                 df,
                 anchors,
                 method_name,
                 positioning_kwargs: dict = {}):
        def method_not_found(**kwargs
                             ):  # just in case we dont have the function
            print('No Function ' + method_name + ' Found!')

        function = getattr(self, method_name, method_not_found)
        return function(df, anchors, **positioning_kwargs)

    def aoa_2(self,
              df,
              anchors,
              to_filter: bool = False,
              filter_kwargs: dict = {},
              **kwargs):
        """Iterates over the DataFrame and calculates
        the intersection of the two most recent measurements.
        Filters measurement if it is too different...
        Does not take into account tags!!!"""

        if to_filter:
            df = filtering.filter_by_history(df.copy(), **filter_kwargs)

        recent_anchors = collections.deque(maxlen=2)
        angle_history = {i: 0 for i in anchors['anchor_id'].unique()}

        timestamps = []
        X, Y = [], []
        used_anchors = []

        for idx, data in df.iterrows():
            anchor_id = data['anchor_id']
            angle_anchor = anchors.loc[anchor_id, 'angle_azimuth']
            angle_measurement = data['angle_azimuth']
            angle = angle_anchor - angle_measurement
            timestamps.append(data['timestamp'])

            if (anchor_id not in recent_anchors or
                (len(recent_anchors) == 2 and anchor_id == recent_anchors[0])):
                recent_anchors.append(anchor_id)
                angle_history[anchor_id] = angle

            if len(recent_anchors) == 2:
                angle_0 = angle_history[recent_anchors[0]]
                angle_1 = angle_history[recent_anchors[1]]

                position_anchor_0 = anchors.loc[recent_anchors[0],
                                                ['x', 'y']].to_numpy()
                position_anchor_1 = anchors.loc[recent_anchors[1],
                                                ['x', 'y']].to_numpy()

                point = calc_line_intersection(angle_0, angle_1,
                                               position_anchor_0,
                                               position_anchor_1)
                if point:
                    x, y = point[0], point[1]
                    X.append(float(x))
                    Y.append(float(y))
                    used_anchors.append(list(recent_anchors))
                else:
                    X.append(np.nan)
                    Y.append(np.nan)
                    used_anchors.append(list(recent_anchors))
            else:
                X.append(np.nan)
                Y.append(np.nan)
                used_anchors.append(['', ''])

        return {
            'est_pos': np.array([X, Y]).T,
            'timestamps': np.array(timestamps),
            #'true_pos': df[['x', 'y']].to_numpy(),
            'used_anchors': list(used_anchors)
        }

    def least_error(self,
                    df,
                    anchors,
                    cheat=False,
                    time_tolerance=250,
                    weight_decrease_base=math.e,
                    **kwargs):
        # Make Complex dataframe for positioning and checking
        processing.add_true_angle(df, anchors)
        df['angle_azimuth_diff'] = df['angle_azimuth_true'] - df[
            'angle_azimuth']
        df = processing.join_anchors(df, anchors)
        processing.add_params(df)
        processing.add_true_params(df)

        # the weight of a time_tolerance old value
        # is 1/weight_decrease_base * as the actual
        tarr = np.sort(df.timestamp.sort_values().unique())
        tsa = []
        posa = []
        posref = []
        erra = []
        eucd = []
        for t in tarr:
            sub = df[df.timestamp <= t]
            if len(sub.anchor_id.unique()) < 2:
                continue
            tsa.append(t)
            # Calculate  weight for measures based on time-difference
            ErWVec = np.power(weight_decrease_base,
                              (1 / time_tolerance) * np.add(sub.timestamp, -t))
            if cheat:
                x, y, e = time_weighted_static_position_true(sub, ErWVec)
            else:
                x, y, e = time_weighted_static_position(sub, ErWVec)
            posa.append((x, y))
            erra.append(e)
            s2 = sub[sub.timestamp == t]
            xr, yr = s2.x.mean(), s2.y.mean()
            posref.append((xr, yr))
            eucd.append(math.sqrt(((xr - x)**2) + ((yr - y)**2)))
        return {
            'est_pos': np.array(posa),
            'timestamps': np.array(tsa),
            'true_pos': np.array(posref),
            'weighted_error': erra,
            'error': eucd
        }

    def least_error_2(self,
                      df,
                      anchors,
                      cheat=False,
                      time_window: int = 1000,
                      time_tolerance=1000,
                      errWfunc='exp',
                      angle_error_tolerance: int = 30,
                      eucledian_error_tolerance: float = 3.0,
                      percentage_error_tolerance: int = None,
                      weight_decrease_base=math.e,
                      min_weight_threshold=0.001,
                      min_measurement_count: int = 20,
                      **kwargs):
        # Make Complex dataframe for positioning and checking
        processing.add_true_angle(df, anchors)
        df['angle_azimuth_diff'] = df['angle_azimuth_true'] - df[
            'angle_azimuth']
        df = processing.join_anchors(df, anchors)
        processing.add_params(df)
        processing.add_true_params(df)

        # the weight of a time_tolerance old value
        # is 1/weight_decrease_base * as the actual
        tarr = np.sort(df.timestamp.sort_values().unique())
        processed_timestamp = []
        estimated_positions = []
        true_positions = []
        weighted_errors = []
        eucledian_errors = []
        x0, y0 = np.nan, np.nan
        n_used_measurements = []

        for t in tarr:
            # Get data for the latest time window
            sub = df[df['timestamp'].between(t - time_window,
                                             t,
                                             inclusive=True)]

            if len(sub) < min_measurement_count or len(
                    sub.anchor_id.unique()) < 2:
                continue

            processed_timestamp.append(t)
            # current true position
            xr, yr = sub.loc[sub.index[-1], ['x', 'y']].to_numpy()

            # Calculate weight for the measurements based on time-difference
            if errWfunc == 'exp':
                ErWVec = np.power(weight_decrease_base, (1 / time_window) *
                                  np.add(sub.timestamp, -t))
            elif errWfunc == 'linear':
                ErWVec = np.linspace(0, 1, len(sub))
                # ErWVec = (-1 / time_tolerance) * np.add(sub.timestamp, -t)
            elif errWfunc == 'power':
                errWfunc = np.power(np.linspace(0.0, 1.0, num=len(sub)),
                                    weight_decrease_base)
            else:  # const
                ErWVec = np.ones(len(sub))

            # Set reference position
            if len(estimated_positions):
                if ~np.isnan(x0) and ~np.isnan(y0):
                    x0, y0 = estimated_positions[-1]
                else:
                    try:
                        x0, y0 = np.nanmedian(estimated_positions, axis=0)
                    except TypeError:
                        print(estimated_positions)

            # Calculate estimated angle error
            # Filter measurements with large error
            if angle_error_tolerance is not None and angle_error_tolerance > 0 and ~np.isnan(
                    x0) and ~np.isnan(y0):
                angle_error = processing.calculate_angle_error(
                    position=np.array([x0, y0]),
                    anchor_position=sub[['x_anchor', 'y_anchor']].to_numpy(),
                    angle=sub['angle_azimuth'].to_numpy(),
                    anchor_angle=sub['angle_azimuth_anchor'].to_numpy())
                if percentage_error_tolerance is not None:
                    angle_error_tolerance = np.percentile(
                        angle_error, percentage_error_tolerance)
                if np.sum(np.abs(angle_error) < angle_error_tolerance
                          ) > min_measurement_count:
                    ErWVec = np.where(
                        np.abs(angle_error) > angle_error_tolerance, 0.0,
                        ErWVec)

            # Calculate estimated eucledian error
            # Filter measurements with large error
            if eucledian_error_tolerance is not None and eucledian_error_tolerance > 0.0 and ~np.isnan(
                    x0) and ~np.isnan(y0):
                euc_error = np.abs(sub['parA'] * x0 + sub['parB'] * y0 +
                                   sub['parC'])
                if percentage_error_tolerance is not None:
                    eucledian_error_tolerance = np.percentile(
                        euc_error, percentage_error_tolerance)
                if np.sum(euc_error < eucledian_error_tolerance
                          ) > min_measurement_count:
                    ErWVec = np.where(euc_error > eucledian_error_tolerance,
                                      0.0, ErWVec)

            # Normalize weights and filter below threshold values
            ErWVec = ErWVec / np.linalg.norm(ErWVec, ord=1)
            # n_used_measurements.append(np.sum(ErWVec > min_weight_threshold))
            if np.sum(ErWVec > min_weight_threshold) > min_measurement_count:
                sub = sub[ErWVec > min_weight_threshold]
                ErWVec = ErWVec[ErWVec > min_weight_threshold]
            # else:
            #     print('No. used measurements:', len(ErWVec))
            #     print(ErWVec)

            if cheat:
                x, y, e = time_weighted_static_position_true(sub, ErWVec)
            else:
                x, y, e = time_weighted_static_position(sub, ErWVec)

            if np.isnan(x) or np.isnan(y):
                estimated_positions.append(estimated_positions[-1])
            else:
                estimated_positions.append((x, y))
            weighted_errors.append(e)
            true_positions.append((xr, yr))
            # euclidean_error = math.sqrt(((xr - x)**2) + ((yr - y)**2))
            # eucledian_errors.append(euclidean_error)

            # print(
            #     f"({x:.1f}, {y:.1f}) -- ({xr:.1f}, {yr:.1f}) -- {euclidean_error:.1f}"
            # )
        # print(
        #     f"No. used measurements: Mean-{np.mean(n_used_measurements)}, Max-{max(n_used_measurements)}"
        # )
        eucledian_errors = processing.euclidean_distance(
            np.array(estimated_positions), np.array(true_positions))
        return {
            'est_pos': np.array(estimated_positions),
            'timestamps': np.array(processed_timestamp),
            'true_pos': np.array(true_positions),
            'weighted_error': weighted_errors,
            'error': eucledian_errors
        }


def calc_line_intersection(angle_0, angle_1, position_anchor_0, position_anchor_1):
    # Convert angles to radians
    angle_0_rad = np.deg2rad(angle_0)
    angle_1_rad = np.deg2rad(angle_1)
    
    # Calculate the slope (tan of the angle) for each line
    m0 = np.tan(angle_0_rad)
    m1 = np.tan(angle_1_rad)
    
    # Using the point-slope form of a line to determine the equations of the lines
    x0, y0 = position_anchor_0
    x1, y1 = position_anchor_1
    
    # Equating the two line equations and solving for x
    x_intersection = (y1 - m1*x1 - y0 + m0*x0) / (m0 - m1)
    
    # Plugging the x value into one of the line equations to get y
    y_intersection = y0 + m0*(x_intersection - x0)
    
    return (x_intersection, y_intersection)


### BP


def evalErr(C, x, y):
    return C[0] * (x**2) + C[1] * (
        y**2) + C[2] * x * y + C[3] * x + C[4] * y + C[5]


def time_weighted_static_position(df, err_weight):
    C = [0, 0, 0, 0, 0, 0]
    C[0] += np.prod([np.square(df.parA), err_weight], axis=0).sum()
    C[1] += np.prod([np.square(df.parB), err_weight], axis=0).sum()
    C[2] += 2 * np.sum(np.prod([df.parA, df.parB, err_weight], axis=0))
    C[3] += 2 * np.sum(np.prod([df.parA, df.parC, err_weight], axis=0))
    C[4] += 2 * np.sum(np.prod([df.parB, df.parC, err_weight], axis=0))
    C[5] += np.prod([np.square(df.parC), err_weight], axis=0).sum()

    x = (C[2] * C[4] - 2 * C[1] * C[3])
    y = (C[2] * C[3] - 2 * C[0] * C[4])
    denominator = ((4 * C[0] * C[1]) - (C[2]**2))
    if denominator > 1e-6:
        x, y = x / denominator, y / denominator
    return (x, y, evalErr(C, x, y))


def time_weighted_static_position_true(df, err_weight):
    C = [0, 0, 0, 0, 0, 0]
    C[0] += np.square(df.parA_true).sum()
    C[1] += np.square(df.parB_true).sum()
    C[2] += 2 * np.sum(np.prod([df.parA_true, df.parB_true], axis=0))
    C[3] += 2 * np.sum(np.prod([df.parA_true, df.parC_true], axis=0))
    C[4] += 2 * np.sum(np.prod([df.parB_true, df.parC_true], axis=0))
    C[5] += np.square(df.parC_true).sum()
    x = (C[2] * C[4] - 2 * C[1] * C[3]) / ((4 * C[0] * C[1]) - (C[2]**2))
    y = (C[2] * C[3] - 2 * C[0] * C[4]) / ((4 * C[0] * C[1]) - (C[2]**2))
    return (x, y, evalErr(C, x, y))
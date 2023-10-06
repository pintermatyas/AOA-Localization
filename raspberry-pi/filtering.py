# Standard library imports.
import traceback
import logging

# Related third party imports.
import numpy as np
import pandas as pd
from scipy.linalg import block_diag
from filterpy.gh import GHFilter
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

# Local application/library specific imports.


class MeasurementFilter:
    def __init__(self) -> None:
        pass

    def filter(self,
               df,
               anchors,
               filter_name,
               filter_kwargs: dict = {},
               log: str = ''):
        # just in case we dont have the function
        def filter_not_found(**kwargs):
            print('No Function ' + filter_name + ' Found!')

        # combined filter
        if '-' in filter_name:
            try:
                new_df = df.copy()
                for name in filter_name.split('-'):
                    filter_function = getattr(self, name + '_filter',
                                              filter_not_found)
                    new_df = filter_function(new_df, anchors, **filter_kwargs)

                return new_df

            except Exception as e:
                print(log)
                logging.error(traceback.format_exc())
                return df

        # single filter
        else:
            filter_function = getattr(self, filter_name + '_filter',
                                      filter_not_found)

            try:
                return filter_function(df, anchors, **filter_kwargs)

            except Exception as e:
                print(log)
                logging.error(traceback.format_exc())
                return df

    def no_filter(self, df, anchors, **kwargs):
        return df

    def history_filter(self,
                       df,
                       anchors,
                       history_length: int = 20,
                       plus_width: int = 5,
                       replace_with: str = 'mean',
                       **kwargs):
        """Filters angle measurements based on their similarity to the history.
        If the angle is out of the
        (min(angle_history) - plus_width, max(angle_history) + plus_width) interval
        then it is replaced according to replace_with"""
        for tag_id in df['tag_id'].unique():
            for anchor_id in df['anchor_id'].unique():
                dfs = df.query("tag_id == @tag_id & anchor_id == @anchor_id")

                if len(dfs) == 0:
                    continue

                measured_angles = dfs['angle_azimuth'].to_list()
                filtered_angles = []

                for idx, angle in enumerate(measured_angles):
                    angle_history = filtered_angles[
                        max(0, idx - history_length):idx]
                    if len(angle_history) >= history_length / 2 and (
                            angle > max(angle_history) + plus_width
                            or angle < min(angle_history) - plus_width):
                        if replace_with == 'last':
                            filtered_angles.append(int(filtered_angles[-1]))
                        elif replace_with == 'mean':
                            filtered_angles.append(
                                np.mean(measured_angles[
                                    max(0, idx - history_length):idx]))
                        else:
                            filtered_angles.append(np.nan)
                    else:
                        filtered_angles.append(angle)

                if len(filtered_angles) == len(measured_angles):
                    df.loc[dfs.index, 'angle_azimuth'] = filtered_angles
                else:
                    print("Shape mis-match... No filtering")
        return df

    def gh_filter(self,
                  df,
                  anchors,
                  history_length: int = 5,
                  plus_width: int = 10,
                  replace_with: str = 'last',
                  **kwargs):
        """Filters angle measurements based on their similarity to the history.
        If the angle is out of the
        (min(angle_history) - plus_width, max(angle_history) + plus_width) interval
        then it is replaced according to replace_with"""
        for tag_id in df['tag_id'].unique():
            for anchor_id in df['anchor_id'].unique():
                dfs = df.query("tag_id == @tag_id & anchor_id == @anchor_id")

                if len(dfs) == 0:
                    continue

                measured_angles = dfs['angle_azimuth'].to_list()
                filtered_angles = []

                for idx, angle in enumerate(measured_angles):
                    angle_history = filtered_angles[
                        max(0, idx - history_length):idx]
                    if len(angle_history) >= history_length / 2 and (
                            angle > max(angle_history) + plus_width
                            or angle < min(angle_history) - plus_width):
                        if replace_with == 'last':
                            filtered_angles.append(int(filtered_angles[-1]))
                        elif replace_with == 'mean':
                            filtered_angles.append(
                                np.mean(measured_angles[
                                    max(0, idx - history_length):idx]))
                        else:
                            filtered_angles.append(np.nan)
                    else:
                        filtered_angles.append(angle)

                if len(filtered_angles) == len(measured_angles):
                    df.loc[dfs.index, 'angle_azimuth'] = filtered_angles
                else:
                    print("Shape mis-match... No filtering")
        return df

    def kalman_filter(self,
                      df,
                      anchors,
                      process_noise: float = 0.1,
                      measurement_variance: float = 10,
                      error_covariance: float = 100.,
                      **kwargs):
        for anchor_id, anchor_df in df.groupby(by='anchor_id'):
            angle_measurements = anchor_df['angle_azimuth'].to_numpy()
            f = KalmanFilter(dim_x=2, dim_z=1)
            f.x = np.array([0., 0.])
            f.F = np.array([[1., 1.], [0., 1.]])
            f.H = np.array([[1., 0.]])
            f.P *= error_covariance
            f.R = measurement_variance
            f.Q = Q_discrete_white_noise(dim=2, dt=0.1, var=process_noise)
            filtered_measurements, _, _, _ = f.batch_filter(angle_measurements)
            df.loc[df['anchor_id'] == anchor_id,
                   'angle_azimuth'] = filtered_measurements[:, 0]
        return df

    def anchor_filter(self, df, anchors, anchor_list: list = [], **kwargs):
        """Removes measurements of anchors in anchor_list."""
        return df[~df['anchor_id'].isin(anchor_list)]

    def rolling_filter(self,
                       df,
                       anchors,
                       window_mean: int = 1,
                       window_median: int = 1,
                       **kwargs):
        for anchor_id, anchor_df in df.groupby(by='anchor_id'):
            df.loc[df['anchor_id'] == anchor_id,
                   'angle_azimuth'] = anchor_df['angle_azimuth'].rolling(
                       window_mean, 1).mean().rolling(window_median,
                                                      1).median()
        return df


class PositionFilter:
    def __init__(self) -> None:
        pass

    def filter(self,
               positions,
               anchors,
               filter_name,
               filter_kwargs: dict = {},
               log: str = ''):
        # just in case we dont have the function
        def filter_not_found(**kwargs):
            print('No Function ' + filter_name + ' Found!')

        # combined filter
        if '-' in filter_name:
            try:
                new_positions = np.copy(positions)
                for name in filter_name.split('-'):
                    filter_function = getattr(self, name + '_filter',
                                              filter_not_found)
                    new_positions = filter_function(new_positions, anchors,
                                                    **filter_kwargs)

                return new_positions

            except Exception as e:
                print(log)
                print(positions)
                logging.error(traceback.format_exc())
                return positions

        # singel filter
        else:
            try:
                filter_function = getattr(self, filter_name + '_filter',
                                          filter_not_found)
                return filter_function(positions, anchors, **filter_kwargs)

            except Exception as e:
                print(log)
                print(positions)
                logging.error(traceback.format_exc())
                return positions

    def no_filter(self, positions, anchors, **kwargs):
        return positions

    def gh_filter(self,
                  positions,
                  anchors,
                  init_length: int = 10,
                  g: float = 0.5,
                  h: float = 0.5,
                  **kwargs):
        """Applies a GH filter to the positions"""
        # Calculating initial position
        x0 = np.median(positions[:init_length], axis=0)
        dx0 = np.array([0.01, 0.01])

        # Applying GH filter to the estimated positions
        f_gh = GHFilter(x=x0, dx=dx0, dt=1., g=g, h=h)
        est_pos_filtered, _ = f_gh.update(positions)

        return est_pos_filtered

    def kalman_filter(self,
                      positions,
                      anchors,
                      init_length: int = 10,
                      dt: float = 1.,
                      position_variance: float = 0.1,
                      measurement_variance: float = 10,
                      error_covariance: float = 100.,
                      **kwargs):

        # Calculating initial position
        init_pos = np.median(positions[:init_length], axis=0)

        # Construct the KalmanFilter object
        filter = KalmanFilter(dim_x=4, dim_z=2)

        # Assign the initial value for the state (position and velocity) [x, vx, y, vy]
        filter.x = np.array([init_pos[0], 0, init_pos[1], 0])

        # Design State Transition Function
        filter.F = np.array([[1, dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, dt],
                             [0, 0, 0, 1]])

        # Design Process Noise Matrix
        q = Q_discrete_white_noise(dim=2, dt=dt, var=position_variance)
        filter.Q = block_diag(q, q)

        # Design Control Function
        filter.B = 0

        # Design Measurement Function
        filter.H = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])

        # Design Measurement Noise Matrix
        filter.R = np.array([[measurement_variance**2, 0],
                             [0, measurement_variance**2]])

        # Design Covariance Matrix
        filter.P = np.eye(filter.F.shape[1]) * error_covariance

        # Run Kalman Filter
        mu, _, _, _ = filter.batch_filter(positions)

        return np.array([mu[:, 0], mu[:, 2]]).T

    def convolve_filter(self, positions, anchors, N: int = 250, **kwargs):

        pos_x = np.convolve(positions[:, 0], np.ones(N) / N, mode='valid')
        pos_y = np.convolve(positions[:, 1], np.ones(N) / N, mode='valid')

        return np.array([pos_x, pos_y]).T

    def rolling_filter(self,
                       positions,
                       anchors,
                       window_mean: int = 100,
                       window_median: int = 100,
                       **kwargs):
        """Simple rolling mean filter length of N"""
        return pd.DataFrame(positions).rolling(window_mean, 1).mean().rolling(
            window_median, 1).median().to_numpy()

    def rectangle_filter(self, positions, anchors, **kwargs):
        pos = np.copy(positions)
        if len(positions) < 1:
            return pos

        xmin, xmax = anchors['x'].min(), anchors['x'].max()
        ymin, ymax = anchors['y'].min(), anchors['y'].max()

        pos[(pos[:, 0] < xmin) | (xmax < pos[:, 0]) | (pos[:, 1] < ymin) |
            (ymax < pos[:, 1])] = np.nan

        return pos


###############################################
#### OLD FILTERS
###############################################


def filter_by_history(df,
                      history_length: int = 20,
                      plus_width: int = 5,
                      replace_with: str = 'mean',
                      **kwargs):
    """Filters angle measurements based on their similarity to the history.
    If the angle is out of the
    (min(angle_history) - plus_width, max(angle_history) + plus_width) interval
    then it is replaced according to replace_with"""
    for tag_id in df['tag_id'].unique():
        for anchor_id in df['anchor_id'].unique():
            dfs = df.query("tag_id == @tag_id & anchor_id == @anchor_id")

            if len(dfs) == 0:
                continue

            measured_angles = dfs['angle_azimuth'].to_list()
            filtered_angles = []

            for idx, angle in enumerate(measured_angles):
                angle_history = filtered_angles[max(0, idx -
                                                    history_length):idx]
                if len(angle_history) >= history_length / 2 and (
                        angle > max(angle_history) + plus_width
                        or angle < min(angle_history) - plus_width):
                    if replace_with == 'last':
                        filtered_angles.append(int(filtered_angles[-1]))
                    elif replace_with == 'mean':
                        filtered_angles.append(
                            np.mean(
                                measured_angles[max(0, idx -
                                                    history_length):idx]))
                    else:
                        filtered_angles.append(np.nan)
                else:
                    filtered_angles.append(angle)

            if len(filtered_angles) == len(measured_angles):
                df.loc[dfs.index, 'angle_azimuth'] = filtered_angles
            else:
                print("Shape mis-match... No filtering")
    return df


def filter_gh(df,
              history_length: int = 5,
              plus_width: int = 10,
              replace_with: str = 'last'):
    """Filters angle measurements based on their similarity to the history.
    If the angle is out of the
    (min(angle_history) - plus_width, max(angle_history) + plus_width) interval
    then it is replaced according to replace_with"""
    for tag_id in df['tag_id'].unique():
        for anchor_id in df['anchor_id'].unique():
            dfs = df.query("tag_id == @tag_id & anchor_id == @anchor_id")

            if len(dfs) == 0:
                continue

            measured_angles = dfs['angle_azimuth'].to_list()
            filtered_angles = []

            for idx, angle in enumerate(measured_angles):
                angle_history = filtered_angles[max(0, idx -
                                                    history_length):idx]
                if len(angle_history) >= history_length / 2 and (
                        angle > max(angle_history) + plus_width
                        or angle < min(angle_history) - plus_width):
                    if replace_with == 'last':
                        filtered_angles.append(int(filtered_angles[-1]))
                    elif replace_with == 'mean':
                        filtered_angles.append(
                            np.mean(
                                measured_angles[max(0, idx -
                                                    history_length):idx]))
                    else:
                        filtered_angles.append(np.nan)
                else:
                    filtered_angles.append(angle)

            if len(filtered_angles) == len(measured_angles):
                df.loc[dfs.index, 'angle_azimuth'] = filtered_angles
            else:
                print("Shape mis-match... No filtering")
    return df
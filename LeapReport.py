import pandas as pd
import numpy as np
import datetime as dt
import Leap_utils as Lp

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from PIL import Image
import cv2

from scipy.signal import savgol_filter

import logging

def interpolate_leap_for_timestamps(leap_df, timestamps):
    """
    Returns a dataframe of the specified timestamps, by interpolating the recorded data.

            Parameters:
                    leap_df (pandas dataframe): Recorded data.
                    timestamps (array of timestamps): Should be the same format as in leap_df

            Returns:
                    leap_df (pandas dataframe): Interpolated data.

    """

    logging.info("Interpolating leap for timestamps")
    # Make a copy of the data as we are going to be making changes

    leap_interpolation_df = leap_df.copy(deep=True)

    # 1. Split by hand_id. Each hand_id is a continuous time that the time has been active
    # 2. Find which timestamps occur within each group.

    leap_hand_id_df = leap_interpolation_df.groupby(by="hand_id")

    interpolated_dfs = []

    for name, group in leap_hand_id_df:

        # Creat an blank dataframe, with the same format as the leap data. But for the number of
        # timestamps that we want to interpolate for.

        timestamps_empty = np.empty((len(timestamps), len(leap_df.columns)))
        timestamps_empty[:] = np.nan
        timestamps_df = pd.DataFrame(data=timestamps_empty, columns=leap_df.columns)
        timestamps_df['timestamp'] = timestamps

        # Only keep those timestamps where hands are present in the data.

        min_timestamp = group['timestamp'].min()
        max_timestamp = group['timestamp'].max()

        timestamps_df = timestamps_df[(timestamps_df['timestamp'] >= min_timestamp) &
                                      (timestamps_df['timestamp'] <= max_timestamp)]

        # Concatenate the two dataframes together, and sort it into a format that is ready for
        # interpolation.

        group = pd.concat([group, timestamps_df], axis=0).sort_values('timestamp')

        group = group.set_index('timestamp')  # needed for cubic interpolation

        numeric_group = group.select_dtypes(exclude='object')  # "hand_id" cannot be interpolated as it is a string

        interpolated_group = numeric_group.interpolate(method='cubic', axis=0)  # interpolate across rows

        group = group.fillna(method="ffill")  # forward fills "hand_id"

        group[interpolated_group.columns] = interpolated_group  # Brings in interpolated data

        group = group.reindex(pd.Index(timestamps_df['timestamp']))  # Remove original data

        interpolated_dfs.append(group)  # This is repeated for each instance of a hand

    return pd.concat(interpolated_dfs, axis=0).sort_values('timestamp')

def plot_leap_with_timestamp(fig, data, timestamp):
    """
    Returns a dataframe of the specified timestamps, by interpolating the recorded data.

            Parameters:
                    leap_df (pandas dataframe): Recorded data.
                    timestamps (array of timestamps): Should be the same format as in leap_df

            Returns:
                    leap_df (pandas dataframe): Interpolated data.

    """
    logging.info("Plot leap with timestamps")


    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim3d(-300, 150)
    ax.set_ylim3d(-300, 150)
    ax.set_zlim3d(-300, 150)

    ax.view_init(125, -140)

    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    if timestamp in data.index.array:

        tracking_event = data.loc[data.index == timestamp, :]

        tracking_event = Lp.get_tracking_event(tracking_event)  # get correct format for plotting

        for hand in tracking_event.hands:
            Lp.plot_hand(hand, ax)


def make_leap_video(filename, framerate, data, timestamps):
    """
    Creates a video from leap motion data, at specified timestamps.

            Parameters:
                    filename (str): filename, must contain extension.
                    framerate (array of timestamps): frames per second the the video will play
                    data (pandas dataframe: leap motion data)
                    timestamps (array): array of timestamps in unix epoch format.

            Returns:
                    None
    """

    logging.info("making leap video")


    # For each timestamp there is either hand data or there isn't.
    # But for each we need to create a frame anyway.

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter(filename, fourcc, framerate, (500, 400))

    for timestamp in timestamps:
        # make a Figure and attach it to a canvas.
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvasAgg(fig)

        plot_leap_with_timestamp(fig, data, timestamp)

        # Retrieve a view on the renderer buffer
        canvas.draw()
        buf = canvas.buffer_rgba()
        # convert to a NumPy array
        x = np.asarray(buf)

        img = Image.fromarray(x.astype(np.uint8))
        opencvimage = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        out.write(opencvimage)
        plt.close(fig)

    out.release()


def plot_leap(ax, leap_timestamps, leap_column, tone_timestamp, y_label):

    logging.info("plotting leap")

    arrowprops = {'width': 1, 'headwidth': 1, 'headlength': 1, 'shrink': 0.05}

    ax.plot(leap_timestamps, leap_column, color='black')

    ymin, ymax = ax.get_ylim()

    ax.axvline(tone_timestamp, alpha=0.5, color='black', label='Auditory tone',
               dashes=(5, 2, 1, 2))
    ax.annotate('Auditory tone', xy=(tone_timestamp, ymax * 0.4), xytext=(-10, 25),
                textcoords='offset points',
                rotation=0, va='bottom', ha='right', annotation_clip=True, arrowprops=arrowprops, backgroundcolor="w")

    ax.grid(color='#F2F2F2', alpha=1, zorder=0)
    ax.set_xticks(np.arange(0, leap_timestamps.max() + 1, step=1))
    ax.set_xlabel('Time ($s$)')
    ax.set_ylabel(y_label)


def create_plot(filename, name, leap_df, tone_timestamp):

    logging.info("creating plot")


    fig, axes = plt.subplots(3, 1)
    fig.set_size_inches(15, 20, forward=True)

    ax_0 = axes[0]
    plot_leap(ax_0, leap_df['timestamp'], leap_df['eculidean_distance'], tone_timestamp, "Distance ($mm$)")

    ax_1 = axes[1]
    plot_leap(ax_1, leap_df['timestamp'], leap_df['velocity'], tone_timestamp, "Speed ($mm$ $s^{-1}$)")

    ax_2 = axes[2]
    plot_leap(ax_2, leap_df['timestamp'], leap_df['acceleration'], tone_timestamp, "Acceleration ($mm$ $s^{-2}$)")

    fig.suptitle(name, fontweight='bold', fontsize=24)

    plt.savefig(filename)


def datetime_string_to_epoch(datetime_string):

    logging.info("datetime string to epoch")

    system_timestamp_utc = dt.datetime.fromisoformat(datetime_string)

    epoch = dt.datetime.utcfromtimestamp(0)

    return (system_timestamp_utc - epoch).total_seconds()

handedness = "right"


def save_report(leap_timestamps_df, leap_data_df, timestamps_data_df, handedness):

    logging.info("saving report")


    handedness = handedness.lower()

    # Load leap timestamps df. Convert both columns to epoch seconds
    leap_timestamps_df['leap_timestamp'] = leap_timestamps_df['leap_timestamp'] * 10 ** - 6  # convert to seconds
    leap_timestamps_df['system_timestamp'] = leap_timestamps_df['system_timestamp'].apply(datetime_string_to_epoch)

    system_timestamp = leap_timestamps_df.iloc[0]['system_timestamp']
    leap_timestamp = leap_timestamps_df.iloc[0]['leap_timestamp']

    # Load leap data. Convert timestamp column to epoch seconds
    leap_data_df['timestamp'] = leap_data_df['timestamp'] * 10 ** - 6
    leap_data_df['timestamp'] = leap_data_df['timestamp'] - leap_timestamp + system_timestamp

    # Filter for only the dominant hand
    leap_data_df = leap_data_df[leap_data_df['hand_type'] == handedness]

    leap_data_df['euclidean_distance'] = leap_data_df[['palm_position_x', 'palm_position_y', 'palm_position_z']].apply(
        np.linalg.norm, axis=1)

    d_time = leap_data_df['timestamp'].diff().fillna(0.)

    leap_data_df['velocity'] = leap_data_df['euclidean_distance'].diff().fillna(0.) / d_time
    leap_data_df['acceleration'] = leap_data_df['velocity'].diff().fillna(0.) / d_time

    leap_data_df['euclidean_distance'] = savgol_filter(leap_data_df['euclidean_distance'] , 33, 3)

    timestamps_data_df = pd.read_csv("20210916-105021_test_17_tone_timestamps.csv", index_col=0)

    # Only successful recordings
    timestamps_data_df = timestamps_data_df[timestamps_data_df["is_success"] == True]

    # Index set to name as they should be unique successful recordings
    timestamps_data_df = timestamps_data_df.set_index('name')

    # Remove Calibration and validation recordings
    timestamps_data_df = timestamps_data_df.filter(like='Reach and Grasp', axis=0)


    for name, row in timestamps_data_df.iterrows():
        start_timestamp = row['start']
        stop_timestamp = row['stop']
        tone_timestamp = row['timestamp']

        current_recording_df = leap_data_df[(leap_data_df['timestamp'] >= start_timestamp) and
                                            leap_data_df['timestamp'] <= stop_timestamp]

        create_plot("report/" + name + ".png", name, current_recording_df, tone_timestamp)

        # Create an array of timestamps at a consistent framerate.

        framerate = 24

        video_timestamps = []

        timestamp = current_recording_df['timestamp'].min()
        while timestamp <= current_recording_df.max():
            video_timestamps.append(timestamp)
            timestamp += 1 / framerate

        video_leap_df = interpolate_leap_for_timestamps(leap_data_df, video_timestamps)

        make_leap_video("report/" + name + ".mp4", 24, video_leap_df, video_timestamps)



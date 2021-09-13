from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtm

from TrialInfoPage import TrialInfoPage
from DemographicPage import DemographicPage
from OldRecordingPage import RecordingPage
from PupilHandler import PupilHandler
from LeapHandler import LeapHandler

import logging
import time
import os
import sys
import configparser
import shutil
import datetime
import pandas as pd
import numpy as np


class TrialWizard(Qtw.QWizard):
    Page_TrialInfo = 1
    Page_Demographic = 2
    Page_Recording = 3

    devices_ready_signal = Qtc.pyqtSignal(dict)

    get_leap_status_signal = Qtc.pyqtSignal()

    start_leap_application_signal = Qtc.pyqtSignal()
    stop_leap_application_signal = Qtc.pyqtSignal()

    def __init__(self, parent=None):
        super(TrialWizard, self).__init__(parent)

        self.setWindowTitle("Reach&Grasp")

        # Declaring a error dialog window to display warning messages.

        self.error_msg = Qtw.QMessageBox()
        self.error_msg.setIcon(Qtw.QMessageBox.Critical)
        self.error_msg.setWindowTitle("Error")
        self.error_dialog = Qtw.QErrorMessage()

        # Declaring variables that are used in the configuration file

        self.drives = []  # Contains a list of drives that the data will be saved to.
        self.local_drive = None  # The letter of the local drive
        self.external_drive = None  # The letter of the external drive
        self.folder_name = None  # A string containing the study name, the parent directory of all patient recordings.

        self.device_config = {"leap": False, "pupil": False}  # Configuration file specifies if the devices are being
        # used. In which case they are set to True.

        self.read_config()  # Read the configuration file

        # Check that there is space available to store the data.

        self.update_drives()

        self.leap_ready = False  # leap_ready and pupil_ready state whether the handlers are ready to record data.
        self.pupil_ready = False

        self.leap_path = None

        # Configuring the pages

        self.setPage(self.Page_Recording, RecordingPage(self))
        self.setPage(self.Page_Demographic, DemographicPage(self))
        self.setPage(self.Page_TrialInfo, TrialInfoPage(self))

        self.setStartId(self.Page_TrialInfo)

        self.setWizardStyle(Qtw.QWizard.ModernStyle)
        self.setPixmap(Qtw.QWizard.LogoPixmap, Qtg.QPixmap('images/clearsky-logo.png'))

        self.setOption(Qtw.QWizard.IndependentPages, True)

        self.startingTime = time.strftime("%Y%m%d-%H%M%S")

        ### LeapRecorder program ###
        if self.device_config['leap']:
            self.leap_process = LeapHandler("LeapRecorder.exe", self.startingTime)
            logging.info("Leap recording process started")

            # Using a thread, needs to be done before we connect signals or slots
            self.leap_thread = Qtc.QThread()
            self.leap_process.moveToThread(self.leap_thread)
            self.leap_thread.start()
            logging.info("Leap Handler moved to thread")

        if self.device_config['pupil']:
            self.pupil_process = PupilHandler()
            # Using a thread, needs to be done before we connect signals or slots
            self.pupil_thread = Qtc.QThread()
            self.pupil_process.moveToThread(self.pupil_thread)
            self.pupil_thread.start()
            logging.info("Pupil Handler moved to thread")

            # Pupil connections
            self.page(self.Page_Recording).pupil_start_calibration.connect(self.pupil_process.start_calibration)
            self.page(self.Page_Recording).pupilStopCalibration.connect(self.pupil_handler.stopCalibration)

            self.page(self.Page_Recording).pupilStartRecording.connect(self.pupil_handler.startRecording)
            self.page(self.Page_Recording).pupilStopRecording.connect(self.pupil_handler.stopRecording)

            self.get_pupil_status.connect(self.pupil_handler.get_status)
            self.pupil_handler.device_status.connect(self.pupil_update)

        logging.info("Completed device setup")
        # Recording Page

        self.devices_ready_signal.connect(self.page(self.Page_Recording).devicesReady)

        # Initial poll
        self.devicesReady()

        # Then update using an interval timer
        interval_seconds = 5
        self.status_timer = Qtc.QTimer()
        self.status_timer.setInterval(interval_seconds * 1000)
        self.status_timer.timeout.connect(self.devicesReady)
        self.status_timer.start()

        logging.info("Initialized QWizard")

    def read_config(self):

        if os.path.exists("config.ini"):

            try:

                logging.info("reading config file")
                config = configparser.ConfigParser()
                config.read("config.ini")

                self.local_drive = config['PATH']['Local']
                self.external_drive = config['PATH']['External']
                self.folder_name = config['PATH']['Folder name']
                self.leap_path = config['PATH']['leap path']

                self.device_config['leap'] = (config['DEVICES']['leap'] == "True")
                self.device_config['pupil'] = (config['DEVICES']['pupil'] == "True")

            except:
                logging.error("Error reading configuration file")

            else:
                logging.info("Successfully read configuration file")

        else:
            logging.error("Config file could not be found")

        logging.info(str(self.device_config))

    def update_drives(self):
        """
        Deals with the errors generated by the get_drives function. If there is no space available at all then the
        program should quit. Otherwise show the messages so that they can be corrected.
        """
        drives_list = []
        error_list = []

        _, _, local_free = shutil.disk_usage(self.local_drive)

        if (local_free / 1073741824) < 2:
            error_list.append('Local disk is low on space')
        else:
            drives_list.append(self.local_drive)

        _, _, external_free = shutil.disk_usage(self.external_drive)

        if (external_free / 1073741824) < 2:
            error_list.append('External disk is low on space')
        else:
            drives_list.append(self.external_drive)

        error_message = '\n'.join(error_list)

        if bool(error_message):

            if len(drives_list) == 0:  # No drives available
                self.error_msg.finished.connect(Qtw.qApp.quit)
                self.error_msg.setText("No drives Available")
                self.error_msg.show()
            else:

                error_message += "\n\nWould you like to continue?"
                reply = Qtw.QMessageBox.question(self, 'Message', error_message, Qtw.QMessageBox.Yes,
                                                 Qtw.QMessageBox.No)

                if reply == Qtw.QMessageBox.No:
                    Qtw.qApp.quit

        self.drives = drives_list

    def devices_ready(self):

        if self.field("intro.leap"):
            self.get_leap_status.emit()
        else:
            self.leap_ready = False

        if self.field("intro.pupil"):
            self.get_pupil_status.emit()
        else:
            self.pupil_ready = False

        self.devices_ready_signal.emit({'leap': self.leap_ready, 'pupil': self.pupil_ready})

    @Qtc.pyqtSlot(bool)
    def leap_update(self, alive):
        # The program will send an update dictionary.

        if not alive:
            logging.error("Leap not active, restarting")
            self.leap_ready = False
            self.start_leap_application_signal.emit()
        else:
            self.leap_ready = True

    @Qtc.pyqtSlot(bool)
    def pupil_update(self, alive):
        if alive:
            self.pupil_ready = True
        else:
            self.pupil_ready = False

    def nextId(self):
        id = self.currentId()

        if id == self.Page_Recording:
            self.page(self.Page_Recording).updatePage()

        if id == self.Page_TrialInfo:
            return self.Page_Demographic
        if id == self.Page_Demographic:
            return self.Page_Recording
        else:
            return -1

    def accept(self):

        participant_id = self.field('intro.participantID')
        filename = self.startingTime + "_" + participant_id

        path = self.folder_name + "\\" + filename + "\\"

        for drive in self.drives:
            os.makedirs(drive + path, exist_ok=True)

        # Update csv

        for drive in self.drives:
            csv_path = drive + self.folder_name + "\\" + "participant_record.csv"
            if not os.path.exists(csv_path):
                participant_record = pd.DataFrame({"ID": [participant_id], "starting time": [self.startingTime]})
                participant_record.to_csv(csv_path)
            else:
                new = pd.DataFrame({"ID": [participant_id], "starting time": [self.startingTime]})
                participant_record_df = pd.read_csv(csv_path, index_col=0)
                participant_record_df = participant_record_df.append(new, ignore_index=True)
                participant_record_df.to_csv(csv_path)

        # MoCA

        intro = {'group': self.field('intro.group'),
                 'handedness': ('intro.handedness'),
                 'moca': self.field('intro.moca'),
                 'srds': self.field('intro.srds'),
                 'acuity': self.field('intro.acuity'),
                 'notes': self.field('intro.notes')}

        intro_df = pd.DataFrame.from_dict(intro, orient='index')

        for drive in self.drives:
            intro_df.to_csv(drive + path + filename + '_intro.csv', header=None)

        # Demographic

        demographic = {'age': self.field('demographic.age'),
                       'sex': self.field('demographic.sex'),
                       'education': self.field('demographic.education')}

        demographic_df = pd.DataFrame.from_dict(demographic, orient='index')

        for drive in self.drives:
            demographic_df.to_csv(drive + path + filename + '_demographics.csv', header=None)

        # Timestamps

        tone_timestamps_df = pd.DataFrame.from_dict(self.page(self.Page_Recording).tone_timestamps, orient='index')
        # tone_timestamps_df.columns = ["recording", "timestamp"]

        for drive in self.drives:
            tone_timestamps_df.to_csv(drive + path + filename + '_tone_timestamps.csv', header=None)

        leap_timestamps_df = pd.DataFrame.from_dict(self.page(self.Page_Recording).leap_timestamps, orient='index')

        for drive in self.drives:
            leap_timestamps_df.to_csv(drive + path + filename + '_leap_timestamps.csv', header=None)

        # Leap motion

        try:
            shutil.rmtree("report")
            os.mkdir("report")
        except FileNotFoundError:
            os.mkdir("report")

        timestamps = self.page(self.Page_Recording).tone_timestamps

        leap_timestamps = self.page(self.Page_Recording).leap_timestamps

        for recording in self.page(self.Page_Recording).leap_recordings:

            if os.path.exists(recording):

                leap_df = pd.read_csv(recording)

                for drive in self.drives:
                    shutil.copyfile(recording, drive + path + filename + '_' + recording.split('\\')[-1])

                while (os.path.exists(recording)):
                    try:
                        os.remove(recording)
                    except:
                        logging.warning("Unable to remove {}".format(recording))

                try:
                    name = recording.split('\\')[-1]
                    name = name.split('.')[0]
                    name = name.replace('_leap', "")

                    auditory_tone_obj = timestamps[name]
                    auditory_tone_seconds = (auditory_tone_obj - datetime(1970, 1, 1)).total_seconds()

                    leap, system = leap_timestamps[name]

                    auditory_tone_seconds = auditory_tone_seconds - float(system)

                    leap_seconds = int(leap) / (10 ** 6)

                    leap_df['timestamp'] = (leap_df['timestamp'] / (10 ** 6)) - leap_seconds

                    leap_min = leap_df['timestamp'].min()

                    if leap_min > 0:
                        leap_df['timestamp'] = leap_df['timestamp'] - leap_min
                        auditory_tone_seconds = auditory_tone_seconds - leap_min

                    leap_df['distance'] = leap_df[['palm_position_x', 'palm_position_y', 'palm_position_z']].apply(
                        np.linalg.norm, axis=1)

                    new_filename = "report/" + name

                    # plot_distance(name, leap_df, auditory_tone_seconds, new_filename)
                except:
                    logging.error("Could not create graph for {}".format(recording))
                else:
                    logging.info("Created graph for {}".format(recording))

        for drive in self.drives:
            shutil.copytree("report/", drive + path + "report\\")

        shutil.rmtree("report/")

        # Pupil Core

        for recording in self.page(self.Page_Recording).pupil_recordings:

            if os.path.exists(recording):

                logging.info("Found recording {}".format(recording))

                for drive in self.drives:
                    shutil.copytree(recording,
                                    drive + path + filename + '_' + recording.split('\\')[-1])
                    logging.info("Copying {} to drive {}".format(recording, drive))

                try:
                    shutil.rmtree(recording)
                except:
                    logging.warning("Unable to delete recording: {}".format(recording))
            else:
                logging.warning("{} recording not found".format(recording))

        logging.info("Successfully saved all recordings")
        super(TrialWizard, self).accept()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(filename='reach&grasp.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.getLogger('matplotlib.font_manager').disabled = True
    logging.info("Starting application")
    app = Qtw.QApplication(sys.argv)
    wizard = TrialWizard()
    wizard.show()
    sys.exit(app.exec_())


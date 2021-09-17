from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtm

from OpenSoftwarePage import OpenSoftwarePage
from TrialInfoPage import TrialInfoPage
from DemographicPage import DemographicPage
from DemonstrationPage import DemonstrationPage
from PupilCoreEyeSetupPage import PupilCoreEyeSetupPage
from DisablePupilDetectionPage import DisablePupilDetectionPage
from CalibrationTutorialPage import CalibrationTutorialPage
from CalibrationPage import CalibrationPage
from RecordingPage import RecordingPage
from RemovePupilCorePage import RemovePupilCorePage
from PupilHandler import PupilHandler
from LeapHandler import LeapHandler

import LeapReport as Lr

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
    def __init__(self, parent=None):
        super(TrialWizard, self).__init__(parent)

        self.setWindowTitle("Reach&Grasp")

        self.setOption(self.HaveHelpButton, False)

        self.startingTime = time.strftime("%Y%m%d-%H%M%S")
        self.leap_handler = LeapHandler("CallbackSample.exe", "temp_recordings/" + self.startingTime)
        self.pupil_handler = PupilHandler()

        try:
            shutil.rmtree("temp_recordings")
            os.mkdir("temp_recordings")
        except FileNotFoundError:
            os.mkdir("temp_recordings")

        self.setWizardStyle(Qtw.QWizard.ModernStyle)
        self.setPixmap(Qtw.QWizard.LogoPixmap, Qtg.QPixmap('images/clearsky-logo.png'))

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
        self.leap_path = None

        self.read_config()  # Read the configuration file

        # Check that there is space available to store the data.

        self.update_drives()

        self.open_software_page_id = self.addPage(OpenSoftwarePage(self))
        self.trial_info_page_id = self.addPage(TrialInfoPage(self))
        demographic_page_id = self.addPage(DemographicPage(self))
        demonstration_page_id = self.addPage(DemonstrationPage(self))
        pupil_core_eye_setup_page_id = self.addPage(PupilCoreEyeSetupPage(self))
        disable_pupil_detection_page_id = self.addPage(DisablePupilDetectionPage(self))
        self.calibration_tutorial_page_id = self.addPage(CalibrationTutorialPage(self))
        self.calibration_page_id = self.addPage(CalibrationPage(self))
        recording_visual_page_id = self.addPage(RecordingPage(self, "Visual "))
        self.remove_pupil_core_page_id = self.addPage(RemovePupilCorePage(self))
        self.recording_memory_page_id = self.addPage(RecordingPage(self, "Memory "))

        self.page(self.calibration_page_id).data_sig.connect(self.data_slot)
        self.page(recording_visual_page_id).data_sig.connect(self.data_slot)
        self.page(self.recording_memory_page_id).data_sig.connect(self.data_slot)

        self.page(self.open_software_page_id).start_connection.connect(self.start_connections)
        self.page(self.calibration_tutorial_page_id).start_pupil_recording.connect(self.start_recording)
        self.page(self.remove_pupil_core_page_id).stop_pupil_recording.connect(self.stop_recording)

        self.data = []

        self.setGeometry(0,0,700,600)
        self.setMinimumSize(700, 800)
        self.setMaximumSize(700, 800)

    @Qtc.pyqtSlot(str, float, float, float, bool)
    def data_slot(self, data_type, start_timestamp, finish_timestamp, tone_timestamp, is_success):
        """
        Receives data from calibration page, and recording pages.

        :param data_type:
        :param start_timestamp:
        :param finish_timestamp:
        :param tone_timestamp:
        :param is_success:
        :return:
        """
        self.data.append([data_type, start_timestamp, finish_timestamp, tone_timestamp, is_success])

    def read_config(self):

        if os.path.exists("config.ini"):

            try:
                logging.info("reading config file")
                config = configparser.ConfigParser()
                config.read("config.ini")

                self.local_drive = config['PATH']['Local']
                self.external_drive = config['PATH']['External']
                self.folder_name = config['PATH']['Folder name']

            except:
                logging.error("Error reading configuration file")

            else:
                logging.info("Successfully read configuration file")

        else:
            logging.error("Config file could not be found")

    def update_drives(self):
        """
        Checks the drives specified in the config file.
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

    def nextId(self) -> int:
        # if self.currentId() == self.trial_info_page_id:
        #     self.pupil_handler.start_connection()
        # if self.currentId() == self.calibration_page_id:
        #     print("hello")
        #     self.pupil_handler.start_recording(self.startingTime)
        if self.currentId() < self.recording_memory_page_id:
            return self.currentId() + 1
        else:
            return -1

    def accept(self):
        """

        When the finish button is pressed this code is executed.

        :return:
        """
        super(TrialWizard, self).accept()

        #self.pupil_handler.stop_recording()
        self.leap_handler.kill_all_open()

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
                 'handedness': self.field('intro.handedness'),
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

        # Data

        timestamps_data_df = pd.DataFrame(self.data, columns=["name", "start", "stop", "timestamp", "is_success"])

        # tone_timestamps_df.columns = ["recording", "timestamp"]

        for drive in self.drives:
            timestamps_data_df.to_csv(drive + path + filename + '_timestamps.csv')

        # Leap timestamps

        leap_timestamps = "temp_recordings/" + self.startingTime + "_leap_timestamps.csv"

        for drive in self.drives:
            shutil.copyfile(leap_timestamps, drive + path + filename + "_leap_timestamps.csv")

        leap_timestamps_df = pd.read_csv(leap_timestamps)

        os.remove(leap_timestamps)

        # Leap motion data

        leap_data = "temp_recordings/" + self.startingTime + "_leap_data.csv"

        for drive in self.drives:
            shutil.copyfile(leap_data, drive + path + filename + "_leap_data.csv")

        leap_data_df = pd.read_csv(leap_data)

        os.remove(leap_data)

        # Create report

        try:
            shutil.rmtree("report")
            os.mkdir("report")
        except FileNotFoundError:
            os.mkdir("report")

        try:
            Lr.save_report(leap_timestamps_df, leap_data_df, timestamps_data_df, intro["handedness"].lower())
        except:
            logging.warning("Unable to save report")
        else:
            logging.info("Successfully created report")

        for drive in self.drives:
            shutil.copytree("report/", drive + path + "report\\")

        shutil.rmtree("report/")

        # Pupil Core

        home = os.path.expanduser("~")
        recording_path = home + "\\recordings\\" + self.startingTime

        if os.path.exists(recording_path):

            logging.info("Found recording {}".format(recording_path))

            for drive in self.drives:
                shutil.copytree(recording_path,
                                drive + path + filename + '_' + recording_path.split('\\')[-1])
                logging.info("Copying {} to drive {}".format(recording_path, drive))

            try:
                shutil.rmtree(recording_path)
            except:
                logging.warning("Unable to delete recording: {}".format(recording_path))
        else:
            logging.warning("{} recording not found".format(recording_path))

        logging.info("Successfully saved all recordings")

        # copy log file

        log_file = "reach&grasp.log"

        for drive in self.drives:
            shutil.copyfile(log_file, drive + path + log_file)




    @Qtc.pyqtSlot()
    def start_connections(self):
        self.leap_handler.start_application()

    @Qtc.pyqtSlot()
    def start_recording(self):
        self.pupil_handler.start_recording(self.startingTime)

    @Qtc.pyqtSlot()
    def stop_recording(self):
        self.pupil_handler.stop_recording()

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

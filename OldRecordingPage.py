import logging
import os
import psutil
import random
import subprocess
import time
from datetime import datetime

from PyQt5 import QtCore as Qtc
from PyQt5 import QtGui as Qtg
from PyQt5 import QtMultimedia as Qtm
from PyQt5 import QtWidgets as Qtw


class RecordingPage(Qtw.QWizardPage):

    pupil_start_recording = Qtc.pyqtSignal(str)
    pupil_stop_recording = Qtc.pyqtSignal()

    pupil_start_calibration = Qtc.pyqtSignal()
    pupil_stop_calibration = Qtc.pyqtSignal()

    def __init__(self, parent=None):
        super(RecordingPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("   ")

        self.tone_timestamps = {}
        self.start_timestamps = {}
        self.stop_timestamps = {}

        self.pupil_recordings = []

        self.current_task = None

        self.leap_ready = False
        self.pupil_ready = False

        self.num_vis = 0
        self.num_mem = 0

        self.tone_player = Qtm.QSoundEffect()
        self.tone_player.setSource(Qtc.QUrl.fromLocalFile("tone.wav"))

        self.error_dialog = Qtw.QErrorMessage()

        self.leap_text_label = Qtw.QLabel("Leap Motion")
        self.leap_image_label = Qtw.QLabel()

        self.leap_device_layout = Qtw.QHBoxLayout()
        self.leap_device_layout.addWidget(self.leap_text_label)
        self.leap_device_layout.addWidget(self.leap_image_label)

        self.pupil_text_label = Qtw.QLabel("Pupil")
        self.pupil_image_label = Qtw.QLabel()

        self.pupil_device_layout = Qtw.QHBoxLayout()
        self.pupil_device_layout.addWidget(self.pupil_text_label)
        self.pupil_device_layout.addWidget(self.pupil_image_label)

        devices_layout = Qtw.QVBoxLayout()
        devices_layout.addLayout(self.leap_device_layout)
        devices_layout.addLayout(self.pupil_device_layout)

        devices_group_box = Qtw.QGroupBox("Devices Ready")
        devices_group_box.setLayout(devices_layout)

        step_one_label = Qtw.QLabel("Make sure that the following programs are open. Ensure that the participants "
                                    "hand is being tracked with the Leap Motion. ")

        leap_visualizer_button = Qtw.QPushButton("Open Leap Visualizer")
        leap_visualizer_button.clicked.connect(self.open_leap_visualizer)

        self.pupil_capture_button = Qtw.QPushButton("Open PupilCapture")
        self.pupil_capture_button.clicked.connect(self.open_pupil_capture)
        self.pupil_calibration_button = Qtw.QPushButton("Start Calibration", checkable=True)

        step_one_layout = Qtw.QVBoxLayout()
        step_one_layout.addWidget(step_one_label)
        step_one_layout.addWidget(leap_visualizer_button)
        step_one_layout.addWidget(self.pupil_capture_button)
        step_one_layout.addWidget(self.pupil_calibration_button)

        step_one_group_box = Qtw.QGroupBox("Step 1:")
        step_one_group_box.setLayout(step_one_layout)

        step_one_a_label = Qtw.QLabel("Once the Pupil Capture software is open. Calibrate using the single Marker")

        self.pupil_calibration_button.clicked.connect(self.calibration_button_toggle)

        step_one_a_layout = Qtw.QVBoxLayout()
        step_one_a_layout.addWidget(step_one_a_label)
        step_one_a_layout.addWidget(self.pupil_calibration_button)

        self.step_one_aGroupBox = Qtw.QGroupBox("Step 1a:")
        self.step_one_aGroupBox.setLayout(step_one_a_layout)

        test_push_button = Qtw.QPushButton("Test Tone")
        test_push_button.clicked.connect(self.tone_player.play)

        step_two_layout = Qtw.QVBoxLayout()

        step_two_label = Qtw.QLabel("This is the tone that will initiate the reach sequence. The participant will reach"
                                    " immediately when hearing the tone.")
        step_two_layout.addWidget(step_two_label)
        step_two_layout.addWidget(test_push_button)

        step_two_group_box = Qtw.QGroupBox("Step 2:")
        step_two_group_box.setLayout(step_two_layout)

        # Radio buttons to select which test is being recorded. These recordings will be added to the arrays. Then the
        # user will be able to add or delete one.

        step_three_label = Qtw.QLabel("Select which test is going to be recorded, the number next to them will indicate"
                                      " the number of recordings that have been made so far.")

        self.visually_guided_radio_button = Qtw.QRadioButton("Visually guided : {}".format(self.num_vis))
        self.memory_guided_radio_button = Qtw.QRadioButton("Memory guided : {}".format(self.num_mem))

        self.visually_guided_radio_button.setChecked(True)

        self.recording_button = Qtw.QPushButton("Start Recording", checkable=True)
        self.recording_button.clicked.connect(self.recording_button_toggle)

        self.status_label = Qtw.QLabel("Ready")

        self.registerField('rec.visually_guided', self.visually_guided_radio_button)
        self.registerField('rec.memory_guided', self.memory_guided_radio_button)

        button_layout = Qtw.QHBoxLayout()
        button_layout.addWidget(self.visually_guided_radio_button)
        button_layout.addWidget(self.memory_guided_radio_button)

        step_three_group_box_layout = Qtw.QVBoxLayout()
        step_three_group_box_layout.addWidget(step_three_label)
        step_three_group_box_layout.addLayout(button_layout)
        step_three_group_box_layout.addWidget(self.recording_button)
        step_three_group_box_layout.addWidget(self.status_label)

        step_three_group_box = Qtw.QGroupBox("Step 3:")
        step_three_group_box.setLayout(step_three_group_box_layout)

        # LAYOUT
        layout = Qtw.QVBoxLayout()
        layout.addWidget(devices_group_box)
        layout.addWidget(step_one_group_box)
        layout.addWidget(self.step_one_aGroupBox)
        layout.addWidget(step_two_group_box)
        layout.addWidget(step_three_group_box)
        self.setLayout(layout)

        self.update_page()

    @Qtc.pyqtSlot(dict)
    def devices_ready(self, devices):
        self.leap_ready = devices['leap']
        self.pupil_ready = devices['pupil']

        tick = Qtg.QPixmap("images/tick.png")
        cross = Qtg.QPixmap("images/cross.png")

        if self.leap_ready:
            self.leap_image_label.setPixmap(tick)
        else:
            self.leap_image_label.setPixmap(cross)

        if self.pupil_ready:
            self.pupil_image_label.setPixmap(tick)
        else:
            self.pupil_image_label.setPixmap(cross)

        if self.field("intro.pupil"):
            self.pupil_text_label.setHidden(False)
            self.pupil_image_label.setHidden(False)
        else:
            self.pupil_text_label.setHidden(True)
            self.pupil_image_label.setHidden(True)

        if self.field("intro.leap"):
            self.leap_text_label.setHidden(False)
            self.leap_image_label.setHidden(False)
        else:
            self.leap_text_label.setHidden(True)
            self.leap_image_label.setHidden(True)

    def play_tone(self):
        """
        This function plays the tone to initiate the reach and grasp task. Before the tone is played a timestamp is
        taken to denote the starting time.
        """

        self.tone_timestamps[self.current_task] = datetime.utcnow()
        self.tone_player.play()
        self.status_label.setText("Tone played, stop when task is completed")
        self.recording_button.setEnabled(True)

    def update_page(self):

        if self.field('intro.pupil'):
            self.pupil_capture_button.setHidden(False)
            self.step_one_aGroupBox.setHidden(False)
        else:
            self.pupil_capture_button.setHidden(True)
            self.step_one_aGroupBox.setHidden(True)

    def open_leap_visualizer(self):
        # if the software is already open then focus it, else open it.

        visualizer_filename = "VRVisualizer.exe"
        path = None
        for root, _, files in os.walk(r"C:\Program Files\Leap Motion"):
            if visualizer_filename in files:
                path = os.path.join(root, visualizer_filename)

        if visualizer_filename not in (p.name() for p in psutil.process_iter()):
            if path is None:
                self.error_dialog.showMessage("Can't find Leap Visualizer program")
            else:
                subprocess.Popen(path)
        else:
            self.error_dialog.showMessage('Vizualizer is already open')

    def open_pupil_capture(self):

        # Recursively find it instead
        # if the software is already open then focus it, else open it.

        filename = "pupil_capture.exe"
        path = None
        for root, _, files in os.walk(r"C:\Program Files (x86)\Pupil-Labs"):
            if filename in files:
                path = os.path.join(root, filename)

        if "pupil_capture.exe" not in (p.name() for p in psutil.process_iter()):
            if path is None:
                self.error_dialog.showMessage("Can't find Pupil Capture program")
            else:
                subprocess.Popen(path)
        else:
            self.error_dialog.showMessage('Pupil  is already open')

    def calibration_button_toggle(self):
        if self.pupil_calibration_button.isChecked():

            if self.field('intro.pupil'):
                if not self.pupil_ready:
                    logging.warning("Pupil was not ready to calibrate")
                    self.pupil_calibration_button.setChecked(False)
                    return

            self.pupil_calibration_button.setText("Stop Calibration")
            self.pupil_start_calibration.emit()
        else:
            self.pupil_calibration_button.setText("Start Calibration")
            self.pupil_stop_calibration.emit()

    def recording_button_toggle(self):
        if self.recording_button.isChecked():
            # Check that the devices which are being used are ready to record.

            if self.field('intro.leap'):
                if not self.leap_ready:
                    # dialog leap not ready
                    logging.warning("Leap was not ready to record")
                    self.recording_button.setChecked(False)
                    return

            if self.field('intro.pupil'):
                if not self.pupil_ready:
                    logging.warning("Pupil was not ready to record")
                    self.recording_button.setChecked(False)
                    return
                elif not self.pupil_calibrated:
                    logging.warning("Didn't start recording as Pupil was not calibrated")
                    return

            self.recording_button.setText("Stop Recording")
            self.recording_button.setEnabled(False)

            if self.field('rec.visually_guided'):
                task = "_visual"
                self.num_vis = self.num_vis + 1
            elif self.field('rec.memory_guided'):
                task = "_memory"
                self.num_mem = self.num_mem + 1
            else:
                task = "_none"

            self.current_task = time.strftime("%Y%m%d-%H%M%S") + task

            if self.field('intro.pupil') and self.pupil_ready:
                self.pupil_start_recording.emit(self.current_task)
                home = os.path.expanduser("~")
                recordings_path = home + "\\recordings\\" + self.current_task
                self.pupil_recordings.append(recordings_path)

            self.start_timestamps[self.current_task] = datetime.utcnow()

            duration = random.randint(3, 7)
            Qtc.QTimer.singleShot(duration * 1000, self.play_tone)
            self.status_label.setText("Recording, wait for tone")

        else:
            if self.field('intro.pupil') and self.pupil_ready:
                self.pupil_stop_recording.emit()

            self.stop_timestamps[self.current_task] = datetime.utcnow()

            self.recording_button.setText("Start Recording")
            self.status_label.setText("Ready")
            self.visually_guided_radio_button.setText("Visually guided : {}".format(self.num_vis))
            self.memory_guided_radio_button.setText("Memory guided : {}".format(self.num_mem))

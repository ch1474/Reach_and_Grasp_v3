from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtmm
from PyQt5 import QtMultimediaWidgets as Qtmmw

import subprocess
import os
import psutil


class OpenSoftwarePage(Qtw.QWizardPage):
    """

    In this page the test administrator is advised how to disable Pupil Tracking.

    """

    start_connection = Qtc.pyqtSignal()

    def __init__(self, parent):
        super(OpenSoftwarePage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        self.error_dialog = Qtw.QErrorMessage()

        page_title = "1. Open required software"
        page_title_label = Qtw.QLabel(page_title)
        page_title_font = Qtg.QFont('times', 15)
        page_title_label.setFont(page_title_font)

        page_text = "Please ensure that Leap Motion Visualizer and Pupil Capture are open and have successfully " \
                    "connected to the devices."
        page_text_label = Qtw.QLabel(page_text, wordWrap=True)

        leap_visualizer_push_button = Qtw.QPushButton("Open Leap Visualizer")
        leap_visualizer_push_button.clicked.connect(self.open_leap_visualizer)
        leap_visualizer_push_button.setMinimumSize(250, 20)

        self.leap_visualizer_image = Qtw.QLabel()
        self.leap_visualizer_image.setPixmap(Qtg.QPixmap("images/cross.png"))

        leap_visualizer_layout = Qtw.QHBoxLayout()
        leap_visualizer_layout.addStretch()
        leap_visualizer_layout.addWidget(leap_visualizer_push_button)
        leap_visualizer_layout.addWidget(self.leap_visualizer_image)
        leap_visualizer_layout.addStretch()

        pupil_capture_push_button = Qtw.QPushButton("Open Pupil Capture")
        pupil_capture_push_button.clicked.connect(self.open_pupil_capture)
        pupil_capture_push_button.setMinimumSize(250, 20)


        self.pupil_capture_image = Qtw.QLabel()
        self.pupil_capture_image.setPixmap(Qtg.QPixmap("images/cross.png"))

        pupil_capture_layout = Qtw.QHBoxLayout()
        pupil_capture_layout.addStretch()
        pupil_capture_layout.addWidget(pupil_capture_push_button)
        pupil_capture_layout.addWidget(self.pupil_capture_image)
        pupil_capture_layout.addStretch()

        page_layout = Qtw.QVBoxLayout()
        page_layout.setSpacing(15)
        page_layout.addWidget(page_title_label)
        page_layout.addWidget(page_text_label)
        page_layout.addLayout(leap_visualizer_layout)
        page_layout.addLayout(pupil_capture_layout)



        self.setLayout(page_layout)

        # Then update using an interval timer
        self.check_software_status()

        interval_seconds = 5
        self.status_timer = Qtc.QTimer()
        self.status_timer.setInterval(interval_seconds * 1000)
        self.status_timer.timeout.connect(self.check_software_status)
        self.status_timer.start()

    def check_software_status(self):
        if "VRVisualizer.exe" in (p.name() for p in psutil.process_iter()):
            self.leap_visualizer_image.setPixmap(Qtg.QPixmap("images/tick.png"))
        else:
            self.leap_visualizer_image.setPixmap(Qtg.QPixmap("images/cross.png"))

        if "pupil_capture.exe" in (p.name() for p in psutil.process_iter()):
            self.pupil_capture_image.setPixmap(Qtg.QPixmap("images/tick.png"))
        else:
            self.pupil_capture_image.setPixmap(Qtg.QPixmap("images/cross.png"))

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
                os.startfile(path)
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
                os.startfile(path)
        else:
            self.error_dialog.showMessage('Pupil  is already open')

    def validatePage(self) -> bool:
        if ("VRVisualizer.exe" in (p.name() for p in psutil.process_iter())) and \
                ("pupil_capture.exe" in (p.name() for p in psutil.process_iter())):
            self.start_connection.emit()
            return True
        else:
            self.error_dialog.showMessage("Programs are not open")
            return False


if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(OpenSoftwarePage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

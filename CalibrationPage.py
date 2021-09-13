from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtmm
from PyQt5 import QtMultimediaWidgets as Qtmmw

import time

class CalibrationPage(Qtw.QWizardPage):
    """

    In this page the test administrator is advised how to disable Pupil Tracking.

    """

    data_sig = Qtc.pyqtSignal(str, float, float, float, bool)

    def __init__(self, parent):
        super(CalibrationPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        self.calibration_1_label = Qtw.QLabel("Calibration 1:")
        self.calibration_1_push_button = Qtw.QPushButton("Start")
        self.calibration_1_push_button.setCheckable(True)
        self.calibration_1_push_button.clicked.connect(lambda: self.pushbutton("Calibration 1", self.calibration_1_push_button))

        self.calibration_2_label = Qtw.QLabel("Calibration 2:")
        self.calibration_2_push_button = Qtw.QPushButton("Start")
        self.calibration_2_push_button.setCheckable(True)
        self.calibration_2_push_button.clicked.connect(lambda: self.pushbutton("Calibration 2", self.calibration_2_push_button))

        self.validation_label = Qtw.QLabel("Validation:")
        self.validation_push_button = Qtw.QPushButton("Start")
        self.validation_push_button.setCheckable(True)
        self.validation_push_button.clicked.connect(lambda: self.pushbutton("Validation", self.validation_push_button))

        page_layout = Qtw.QVBoxLayout()
        page_layout.addWidget(self.calibration_1_label)
        page_layout.addWidget(self.calibration_1_push_button)
        page_layout.addWidget(self.calibration_2_label)
        page_layout.addWidget(self.calibration_2_push_button)
        page_layout.addWidget(self.validation_label)
        page_layout.addWidget(self.validation_push_button)

        self.setLayout(page_layout)

        self.continue_message_box = Qtw.QMessageBox()

        self.start_time = None

    def validatePage(self) -> bool:

        if (self.start_time is None) and \
        (not self.calibration_1_push_button.isEnabled()) and \
        (not self.calibration_2_push_button.isEnabled()) and \
        (not self.validation_push_button.isEnabled()):
            return True
        else:
            ret = self.continue_message_box.question(self, "Warning", "Not all calibrations have been made. Continue?")

            if ret == self.continue_message_box.Yes:
                return True
            else:
                return False


    def pushbutton(self, type, button):

        if button.isChecked():
            if self.start_time is not None:
                button.toggle()
            else:
                self.start_time = time.time()
                button.setText("Stop")
        else:
            button.setText("Start")
            stop_time = time.time()
            ret = self.continue_message_box.question(self, "Continue?", type + " successful?")

            if ret == self.continue_message_box.Yes:
                # emit signal
                button.setText("Done!")
                button.setDisabled(True)

                self.data_sig.emit(type, self.start_time, stop_time, 0.0, True)
            else:
                self.data_sig.emit(type, self.start_time, stop_time, 0.0, False)

            self.start_time = None


if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(CalibrationPage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

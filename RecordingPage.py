from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtmm
from PyQt5 import QtMultimediaWidgets as Qtmmw

import time
import random


class RecordingPage(Qtw.QWizardPage):
    """

    In this page the test administrator is advised how to disable Pupil Tracking.

    """

    data_sig = Qtc.pyqtSignal(str, float, float, float, bool)

    def __init__(self, parent, test_type):
        super(RecordingPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        if test_type == "Memory ":
            page_title = Qtw.QLabel("11. Memory assessment")
            page_title_font = Qtg.QFont('Times', 15)
            page_title.setFont(page_title_font)
        else:
            page_title = Qtw.QLabel("9. Visual assessment")
            page_title_font = Qtg.QFont('Times', 15)
            page_title.setFont(page_title_font)


        self.button_label_1 = Qtw.QLabel(test_type + "Reach and Grasp 1:")
        self.push_button_1 = Qtw.QPushButton("Start")
        self.push_button_1.setCheckable(True)
        self.push_button_1.clicked.connect(lambda: self.pushbutton(test_type + "Reach and Grasp 1", self.push_button_1))

        self.label_2 = Qtw.QLabel(test_type + "Reach and Grasp 2:")
        self.push_button_2 = Qtw.QPushButton("Start")
        self.push_button_2.setCheckable(True)
        self.push_button_2.clicked.connect(lambda: self.pushbutton(test_type + "Reach and Grasp 2", self.push_button_2))

        self.label_3 = Qtw.QLabel(test_type + "Reach and Grasp 3:")
        self.push_button_3 = Qtw.QPushButton("Start")
        self.push_button_3.setCheckable(True)
        self.push_button_3.clicked.connect(lambda: self.pushbutton(test_type + "Reach and Grasp 3", self.push_button_3))

        self.label_4 = Qtw.QLabel(test_type + "Reach and Grasp 4:")
        self.push_button_4 = Qtw.QPushButton("Start")
        self.push_button_4.setCheckable(True)
        self.push_button_4.clicked.connect(lambda: self.pushbutton(test_type + "Reach and Grasp 4", self.push_button_4))

        self.label_5 = Qtw.QLabel(test_type + "Reach and Grasp 5:")
        self.push_button_5 = Qtw.QPushButton("Start")
        self.push_button_5.setCheckable(True)
        self.push_button_5.clicked.connect(lambda: self.pushbutton(test_type + "Reach and Grasp 5", self.push_button_5))

        page_layout = Qtw.QVBoxLayout()
        page_layout.setSpacing(15)
        page_layout.addWidget(page_title)
        page_layout.addWidget(self.button_label_1)
        page_layout.addWidget(self.push_button_1)
        page_layout.addWidget(self.label_2)
        page_layout.addWidget(self.push_button_2)
        page_layout.addWidget(self.label_3)
        page_layout.addWidget(self.push_button_3)
        page_layout.addWidget(self.label_4)
        page_layout.addWidget(self.push_button_4)
        page_layout.addWidget(self.label_5)
        page_layout.addWidget(self.push_button_5)

        self.setLayout(page_layout)

        self.continue_message_box = Qtw.QMessageBox()

        self.tone_player = Qtmm.QSoundEffect()
        self.tone_player.setSource(Qtc.QUrl.fromLocalFile("tone.wav"))

        self.tone_timestamp = None

        self.start_time = None

    def validatePage(self) -> bool:

        if (self.start_time is None) and \
        (not self.push_button_1.isEnabled()) and \
        (not self.push_button_2.isEnabled()) and \
        (not self.push_button_3.isEnabled()) and \
        (not self.push_button_4.isEnabled()) and \
        (not self.push_button_5.isEnabled()):
            return True
        else:
            ret = self.continue_message_box.question(self, "Warning", "Not all recordings have been made. Continue?")

            if ret == self.continue_message_box.Yes:
                return True
            else:
                return False


    def play_tone(self, button):
        """
        This function plays the tone to initiate the reach and grasp task. Before the tone is played a timestamp is
        taken to denote the starting time.
        """

        self.tone_timestamp = time.time()
        self.tone_player.play()
        button.setDisabled(False)
        button.setText("Tone played, stop when task is completed")

    def pushbutton(self, button_type, button):

        if button.isChecked():
            if self.start_time is not None:
                button.toggle()
            else:
                self.start_time = time.time()

                duration = random.randint(3, 7)
                Qtc.QTimer.singleShot(duration * 1000, lambda: self.play_tone(button))
                button.setText("Wait for tone")
                button.setDisabled(True)
        else:
            button.setText("Start")
            stop_time = time.time()
            ret = self.continue_message_box.question(self, "Continue?", button_type + " successful?")

            if ret == self.continue_message_box.Yes:
                # emit signal
                button.setText("Done!")
                button.setDisabled(True)

                self.data_sig.emit(button_type, self.start_time, stop_time, self.tone_timestamp, True)
            else:
                self.data_sig.emit(button_type, self.start_time, stop_time, self.tone_timestamp, False)

            self.start_time = None


if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(RecordingPage(wizard, "Visual "))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

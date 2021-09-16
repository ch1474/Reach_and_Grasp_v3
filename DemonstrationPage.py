from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtmm

import time
import random

class DemonstrationPage(Qtw.QWizardPage):

    """
    In this section the assessment administrator will be instructing the participant. To do this a button is provided
    that will play the same tone as in the experiment.

    """

    def __init__(self, parent):
        super(DemonstrationPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        page_title = "4. Demonstrate reach and grasp"
        page_title_label = Qtw.QLabel(page_title)
        page_title_font = Qtg.QFont('times', 15)
        page_title_label.setFont(page_title_font)

        page_text = "Please demonstrate to the patient the procedure for the experiment, as stated in the " \
                    "documentation. A button is provided which plays the stimulus tone after an interval. "

        page_text_label = Qtw.QLabel(page_text, wordWrap=True)

        self.continue_message_box = Qtw.QMessageBox()

        self.tone_player = Qtmm.QSoundEffect()
        self.tone_player.setSource(Qtc.QUrl.fromLocalFile("tone.wav"))

        self.button_label_1 = Qtw.QLabel("Demonstration button:")
        self.push_button_1 = Qtw.QPushButton("Start")
        self.push_button_1.setCheckable(True)
        self.push_button_1.clicked.connect(lambda: self.pushbutton(self.push_button_1))

        layout = Qtw.QVBoxLayout()
        layout.setSpacing(15)
        layout.addWidget(page_title_label)
        layout.addWidget(page_text_label)
        layout.addWidget(self.button_label_1)
        layout.addWidget(self.push_button_1)

        self.setLayout(layout)

        self.start_time = None

    def play_tone(self, button):
        """
        This function plays the tone to initiate the reach and grasp task. Before the tone is played a timestamp is
        taken to denote the starting time.
        """

        self.tone_timestamp = time.time()
        self.tone_player.play()
        button.setDisabled(False)
        button.setText("Tone played, stop when task is completed")

    def pushbutton(self, button):

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
            ret = self.continue_message_box.question(self, "Continue?", " Demonstration successful?")

            if ret == self.continue_message_box.Yes:
                # emit signal
                button.setText("Done!")
                button.setDisabled(True)

            self.start_time = None

if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(DemonstrationPage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

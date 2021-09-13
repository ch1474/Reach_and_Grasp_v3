from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtmm
from PyQt5 import QtMultimediaWidgets as Qtmmw


class GifLayout(Qtw.QVBoxLayout):

    def __init__(self, heading, text, gifs):
        super(GifLayout, self).__init__()

        label_heading_font = Qtg.QFont('Times', 10)
        label_heading_font.setBold(True)
        self.label_heading = Qtw.QLabel(heading)
        self.label_heading.setFont(label_heading_font)

        self.text_label = Qtw.QLabel(text, wordWrap=True)

        self.addWidget(self.label_heading)
        self.addWidget(self.text_label)

        # set qmovie as label
        for gif in gifs:
            self.gif_label = Qtw.QLabel()
            self.gif = Qtg.QMovie(gif)
            self.gif_label.setMovie(self.gif)
            self.gif.start()
            self.addWidget(self.gif_label)

        self.setSpacing(20)
        self.addStretch()


class DisablePupilDetectionPage(Qtw.QWizardPage):
    """

    In this page the test administrator is advised how to disable Pupil Tracking.

    """

    def __init__(self, parent):
        super(DisablePupilDetectionPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        self.disable_text = "Pupil detection is disabled to ensure the stability of the recording. Go to <b>General " \
                            "settings</b> in Pupil Capture and turn off <b>Pupil detection</b> as shown below. "

        self.disable_gif = GifLayout("Disable Pupil Detection", self.disable_text,
                                     ["gifs/turning_off_pupil_detection.gif"])


        self.setLayout(self.disable_gif)


if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(DisablePupilDetectionPage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

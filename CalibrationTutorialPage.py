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


class CalibrationTutorialPage(Qtw.QWizardPage):
    """

    In this page the test administrator is advised how to position the eye camera.

    """
    start_pupil_recording = Qtc.pyqtSignal()

    def __init__(self, parent):
        super(CalibrationTutorialPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        page_title = Qtw.QLabel("Calibration and Validation Information")
        page_title_font = Qtg.QFont('Times', 20)
        page_title_font.setBold(True)
        page_title.setFont(page_title_font)

        page_text = "In order to know what someone is looking at, we must establish a mapping between pupil and gaze " \
                    "positions. This is what we call calibration. The calibration process establishes a mapping from " \
                    "pupil to gaze coordinates. "

        page_text_label = Qtw.QLabel(page_text, wordWrap=True)

        # Calibration (This is repeated twice)

        # 1. Prop the calibration marker on the object, such that the target is facing the user.
        # 2. Ask the patient to gaze at the center of the marker.
        # 3. Turn the calibration marker around.


        calibration_heading = Qtw.QLabel("Calibration")
        calibration_heading_font = Qtg.QFont('Times', 15)
        calibration_heading_font.setBold(True)
        calibration_heading.setFont(calibration_heading_font)

        calibration_text_1 = "1.\tProp the calibration marker on the object, such that the target is facing the user"
        calibration_label_1 = Qtw.QLabel(calibration_text_1, wordWrap=True)

        calibration_start_image_label = Qtw.QLabel()
        calibration_start_image = Qtg.QPixmap("images/calibration_start.jpg")
        calibration_start_image_label.setPixmap(calibration_start_image)

        head_motion_text = '2.\tGaze at the center of the marker and slowly move your head in a spiral motion. You can ' \
                           'also move ' \
                           'your head in other patterns. This choreography enables you to quickly sample a wide range ' \
                           'of gaze angles and cover a large range of your FOV. '


        head_motion_label = Qtw.QLabel(head_motion_text, wordWrap=True)

        head_spiral_label = Qtw.QLabel()
        head_spiral_gif = Qtg.QMovie("gifs/head_spiral.gif")
        head_spiral_label.setMovie(head_spiral_gif)
        head_spiral_gif.start()

        calibration_step_3_text = "2.\t Turn the calibration marker around to stop calibration"

        calibration_step_3_label = Qtw.QLabel(calibration_step_3_text, wordWrap=True)

        calibration_stop_image_label = Qtw.QLabel()
        calibration_stop_image = Qtg.QPixmap("images/calibration_finish.jpg")
        calibration_stop_image_label.setPixmap(calibration_stop_image)


        # Validation

        # 1. Ask the patient to follow the marker as the accessor moves it around the table.
        # 2. Once the marker has moved then

        validation_heading = Qtw.QLabel("Validation")
        validation_heading_font = Qtg.QFont('Times', 15)
        validation_heading_font.setBold(True)
        validation_heading.setFont(validation_heading_font)

        validation_text = "Ask the patient to follow the marker as the test administrator moves it in a circular motion around the table.\n\n Once the marker has finished moving then flip it over to finish validation."

        validation_text_label = Qtw.QLabel(validation_text, wordWrap=True)

        validation_label = Qtw.QLabel()
        validation_gif = Qtg.QMovie("gifs/validation.gif")
        validation_label.setMovie(validation_gif)
        validation_gif.start()

        self.page_layout = Qtw.QVBoxLayout()
        self.page_layout.addWidget(calibration_heading)
        self.page_layout.addWidget(calibration_label_1)
        self.page_layout.addWidget(calibration_start_image_label)
        self.page_layout.addWidget(head_motion_label)
        self.page_layout.addWidget(head_spiral_label)
        self.page_layout.addWidget(calibration_step_3_label)
        self.page_layout.addWidget(calibration_stop_image_label)
        self.page_layout.addWidget(validation_heading)
        self.page_layout.addWidget(validation_text_label)
        self.page_layout.addWidget(validation_label)

        self.page_container_widget = Qtw.QWidget()
        self.page_container_widget.setLayout(self.page_layout)

        self.scroll_area = Qtw.QScrollArea()

        # Scroll Area Properties
        self.scroll_area.setVerticalScrollBarPolicy(Qtc.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qtc.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setWidget(self.page_container_widget)

        self.page_layout2 = Qtw.QVBoxLayout()
        self.page_layout2.addWidget(page_title)
        self.page_layout2.addWidget(page_text_label)
        self.page_layout2.addWidget(self.scroll_area)

        self.setLayout(self.page_layout2)

        self.continue_message_box = Qtw.QMessageBox()

    def validatePage(self) -> bool:
        ret = self.continue_message_box.question(self,"Continue?","Ready to continue? Pupil Core will start recording")

        if ret == self.continue_message_box.Yes:
            self.start_pupil_recording.emit()
            return True
        else:
            return False

if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(CalibrationTutorialPage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

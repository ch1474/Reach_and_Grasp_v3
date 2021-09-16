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


class PupilCoreEyeSetupPage(Qtw.QWizardPage):
    """

    In this page the test administrator is advised how to position the eye camera.

    """

    def __init__(self, parent):
        super(PupilCoreEyeSetupPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        page_title = Qtw.QLabel("5. Checking pupil detection")
        page_title_font = Qtg.QFont('Times', 15)
        page_title.setFont(page_title_font)

        page_text =  "Please place the Pupil Core on the patient. Capturing good raw videos of the eyes is essential " \
                     "for successful eye tracking with the " \
                     "Pupil Core.\n\nThis page details how to physically adjust the eye cameras on the Pupil Core " \
                     "headset to get good images of the eyes."
        page_text_label = Qtw.QLabel(page_text, wordWrap=True)

        pupil_detection_text = "Take a look at the eye windows.\n\nPupil Core " \
                               "uses a 3D model of the eye to improve the pupil detection. Adjust the eye cameras " \
                               "such that your pupil is always visible, even when looking at extreme angles."

        self.pupil_detection_gif = GifLayout("Verifying Pupil Detection", pupil_detection_text, ["gifs/pupil_tracking.gif"])

        pupil_detection_extended_text = '<p><b>Slowly move your eyes around until the eye model (green circle) is ' \
                                        'adjusted to ' \
                                        'fit your eye ball.</b> If everything is set up properly, you should see a ' \
                                        'green ' \
                                        'circle around the eye ball and a red circle around the pupil with a red dot ' \
                                        'in the center (colours vary with software versions).</p><p>Next, check the world window.</p><p>You will see confidence ' \
                                        'graphs ' \
                                        'in the top for each eye. 1.0 = high confidence pupil detection. 0.0 = no ' \
                                        'confidence.</p>'

        self.pupil_detection_more_text = Qtw.QLabel(pupil_detection_extended_text, wordWrap=True)

        pupil_adjustments = Qtw.QLabel("Pupil Core Adjustments")
        pupil_adjustments_font = Qtg.QFont('Times', 15)
        #pupil_adjustments_font.setBold(True)
        pupil_adjustments.setFont(pupil_adjustments_font)

        arm_text = "The eye camera arm slides in and out of the headset frame. You can slide the eye camera arm along the track."
        self.arm_gif = GifLayout("Slide Eye Camera", arm_text, ["gifs/arm_sliding.gif"])

        rotate_eye_camera_text = "The eye camera arm is connected to the eye camera via the ball joint. You can rotate " \
                                 "about its ball joint. There are 6 degrees of freedom to the ball joint. Try twisting and " \
                                 "hinging movements to get a good image of the eye. "

        self.rotate_eye_camera_gif = GifLayout("Rotate Eye Camera", rotate_eye_camera_text,
                                               ["gifs/eye_camera_rotation_hinge.gif",
                                                "gifs/eye_camera_rotation_twist.gif"])

        world_camera_text = "You can rotate the world camera up and down to align with your FOV. Set the focus for " \
                            "the distance at which you will be calibrating by rotating the camera lens. "

        self.world_camera_gif = GifLayout("World Camera", world_camera_text, ["gifs/world_camera_rotation.gif",
                                                                              "gifs/world_camera_focus.gif"])

        self.adjustments_scroll = Qtw.QScrollArea()

        # Scroll Area Properties
        self.adjustments_scroll.setVerticalScrollBarPolicy(Qtc.Qt.ScrollBarAlwaysOn)
        self.adjustments_scroll.setHorizontalScrollBarPolicy(Qtc.Qt.ScrollBarAlwaysOff)
        self.adjustments_scroll.setWidgetResizable(True)
        self.adjustments_scroll.setMinimumSize(510, 500)

        self.adjustments_layout = Qtw.QVBoxLayout()
        self.adjustments_layout.setSpacing(15)
        self.adjustments_layout.addLayout(self.pupil_detection_gif)
        self.adjustments_layout.addWidget(self.pupil_detection_more_text)
        self.adjustments_layout.addWidget(pupil_adjustments)
        self.adjustments_layout.addLayout(self.arm_gif)
        self.adjustments_layout.addLayout(self.rotate_eye_camera_gif)
        self.adjustments_layout.addLayout(self.world_camera_gif)
        self.adjustments_layout.addStretch()

        self.adjustments_container = Qtw.QWidget()
        self.adjustments_container.setLayout(self.adjustments_layout)

        self.adjustments_scroll.setWidget(self.adjustments_container)



        self.page_layout = Qtw.QVBoxLayout()
        self.page_layout.setSpacing(15)
        self.page_layout.addWidget(page_title)
        self.page_layout.addWidget(page_text_label)
        self.page_layout.addWidget(self.adjustments_scroll)
        self.setLayout(self.page_layout)


if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(PupilCoreEyeSetupPage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc
from PyQt5 import QtMultimedia as Qtmm
from PyQt5 import QtMultimediaWidgets as Qtmmw


class RemovePupilCorePage(Qtw.QWizardPage):
    """

    In this page the test administrator is advised how to disable Pupil Tracking.

    """

    def __init__(self, parent):
        super(RemovePupilCorePage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        page_title = Qtw.QLabel("10. Remove Pupil Core")
        page_title_font = Qtg.QFont('Times', 15)
        page_title.setFont(page_title_font)

        page_text = "Please remove the Pupil core from the patient, and place on the blindfold for the memory task."
        page_text_label = Qtw.QLabel(page_text)

        page_image_label = Qtw.QLabel()
        page_image = Qtg.QPixmap("images/blindfold.jpg")
        page_image_label.setPixmap(page_image)

        page_layout = Qtw.QVBoxLayout()
        page_layout.setSpacing(15)
        page_layout.addWidget(page_title)
        page_layout.addWidget(page_text_label)
        page_layout.addWidget(page_image_label)

        self.setLayout(page_layout)

if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(RemovePupilCorePage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()


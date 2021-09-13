from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc


class DemonstrationPage(Qtw.QWizardPage):

    """
    In this section the assessment administrator will be instructing the participant. To do this a button is provided
    that will play the same tone as in the experiment.

    """

    def __init__(self, parent):
        super(DemonstrationPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")


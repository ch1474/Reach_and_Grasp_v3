from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc


class DemographicPage(Qtw.QWizardPage):
    def __init__(self, parent=None):
        super(DemographicPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        age_line_edit = Qtw.QLineEdit()
        age_line_edit.setValidator(Qtg.QRegExpValidator(Qtc.QRegExp("[0-9]*[.]*[0-9]*")))

        sex_combo_box = Qtw.QComboBox()
        sex_combo_box.addItem('M', 'M')
        sex_combo_box.addItem('F', 'F')

        education_line_edit = Qtw.QLineEdit()
        education_line_edit.setValidator(Qtg.QRegExpValidator(Qtc.QRegExp("[0-9]*[.][0-9]*")))

        self.registerField('demographic.age', age_line_edit)
        self.registerField('demographic.sex', sex_combo_box, "currentText")
        self.registerField('demographic.education', education_line_edit)

        layout = Qtw.QFormLayout()
        layout.addRow("Age", age_line_edit)
        layout.addRow("Sex", sex_combo_box)
        layout.addRow("Years of education", education_line_edit)
        self.setLayout(layout)

from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc


class DemographicPage(Qtw.QWizardPage):
    def __init__(self, parent=None):
        super(DemographicPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        page_title = "3. Demographic information"
        page_title_label = Qtw.QLabel(page_title)
        page_title_font = Qtg.QFont('times', 15)
        page_title_label.setFont(page_title_font)

        page_text = "Please enter the specified information in the form."
        page_text_label = Qtw.QLabel(page_text, wordWrap=True)

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

        form_layout = Qtw.QFormLayout()
        form_layout.setSpacing(15)
        form_layout.addRow("Age", age_line_edit)
        form_layout.addRow("Sex", sex_combo_box)
        form_layout.addRow("Years of education", education_line_edit)

        page_layout = Qtw.QVBoxLayout()
        page_layout.setSpacing(15)
        page_layout.addWidget(page_title_label)
        page_layout.addWidget(page_text_label)
        page_layout.addLayout(form_layout)

        self.setLayout(page_layout)


if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(DemographicPage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc


class TrialInfoPage(Qtw.QWizardPage):

    def __init__(self, parent):
        super(TrialInfoPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

        page_title = "2. Patient information"
        page_title_label = Qtw.QLabel(page_title)
        page_title_font = Qtg.QFont('times', 15)
        page_title_label.setFont(page_title_font)

        page_text = "Please enter the specified information in the form. Enter any additional information in the " \
                    "notes section. An ID is required to continue. "
        page_text_label = Qtw.QLabel(page_text, wordWrap=True)

        participant_id_line_edit = Qtw.QLineEdit()

        group_combo_box = Qtw.QComboBox()
        group_combo_box.addItem('Alzheimer\'s Disease', 'Alzheimer\'s Disease')
        group_combo_box.addItem('Parkinson\'s Disease', 'Parkinson\'s Disease')
        group_combo_box.addItem('Vascular Dementia', 'Vascular Dementia')
        group_combo_box.addItem('MCI', 'MCI')
        group_combo_box.addItem('Control', 'Control')
        group_combo_box.addItem('Other', 'Other')

        handedness_combo_box = Qtw.QComboBox()
        handedness_combo_box.addItem('Right', 'Right')
        handedness_combo_box.addItem('Left', 'Left')

        moca_spin_box = Qtw.QSpinBox(maximum=30)
        srds = Qtw.QSpinBox(maximum=80)

        acuity_line_edit = Qtw.QLineEdit()
        acuity_line_edit.setValidator(Qtg.QRegExpValidator(Qtc.QRegExp("[-]*[0-9]*[.][0-9]*")))

        notes_plain_text_edit = Qtw.QPlainTextEdit()

        self.registerField('intro.participantID*', participant_id_line_edit)
        self.registerField('intro.group', group_combo_box, "currentText")
        self.registerField('intro.handedness', handedness_combo_box, "currentText")
        self.registerField('intro.moca', moca_spin_box)
        self.registerField('intro.srds', srds)
        self.registerField('intro.acuity', acuity_line_edit)
        self.registerField('intro.notes', notes_plain_text_edit, "plainText")

        form_layout = Qtw.QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.addRow("Participant ID", participant_id_line_edit)
        form_layout.addRow("Group", group_combo_box)
        form_layout.addRow("Handedness", handedness_combo_box)
        form_layout.addRow("MoCA Total Score", moca_spin_box)
        form_layout.addRow("SRDS Total Score", srds)
        form_layout.addRow("Visual Acuity Score (If applicable)", acuity_line_edit)
        form_layout.addRow("Notes", notes_plain_text_edit)

        page_layout = Qtw.QVBoxLayout()
        page_layout.setSpacing(15)
        page_layout.addWidget(page_title_label)
        page_layout.addWidget(page_text_label)
        page_layout.addLayout(form_layout)
        self.setLayout(page_layout)


if __name__ == "__main__":
    app = Qtw.QApplication([])

    wizard = Qtw.QWizard()
    wizard.addPage(TrialInfoPage(wizard))

    wizard.setWindowTitle("Trivial Wizard")
    wizard.show()

    app.exec()

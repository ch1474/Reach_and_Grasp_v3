from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtGui as Qtg
from PyQt5 import QtCore as Qtc


class TrialInfoPage(Qtw.QWizardPage):

    def __init__(self, parent):
        super(TrialInfoPage, self).__init__(parent)

        self.setTitle("  ")
        self.setSubTitle("  ")

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

        layout = Qtw.QFormLayout()
        layout.setVerticalSpacing(15)
        layout.addRow("Participant ID", participant_id_line_edit)
        layout.addRow("Group", group_combo_box)
        layout.addRow("Handedness", handedness_combo_box)
        layout.addRow("MoCA Total Score", moca_spin_box)
        layout.addRow("SRDS Total Score", srds)
        layout.addRow("Visual Acuity Score (If applicable)", acuity_line_edit)
        layout.addRow("Notes", notes_plain_text_edit)

        layout_group_box = Qtw.QGroupBox()
        layout_group_box.setLayout(layout)

        widget_layout = Qtw.QVBoxLayout()
        widget_layout.addWidget(layout_group_box)
        self.setLayout(widget_layout)

import subprocess

from PyQt5 import QtCore as Qtc


class LeapHandler(Qtc.QObject):
    device_status = Qtc.pyqtSignal(bool)

    def __init__(self, application_name, filename):
        super().__init__()
        self.application_name = application_name
        self.filename = filename
        self.process = None

    def get_status(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.device_status.emit(True)
            else:
                self.device_status.emit(True)
        else:
            self.device_status.emit(False)

    def start_application(self):
        if self.process is None:
            self.process = subprocess.Popen([self.application_name, self.filename])

    def stop_application(self):
        if self.process is not None:
            self.process.terminate()

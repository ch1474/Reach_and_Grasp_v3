import subprocess
import os
import time
import psutil

from PyQt5 import QtCore as Qtc


class LeapHandler(Qtc.QObject):
    device_status = Qtc.pyqtSignal(bool)

    def __init__(self, application_name, filename):
        super().__init__()
        self.application_name = application_name
        self.filename = filename
        self.process = None
        self.kill_all_open()

    def start_application(self):
        if self.process is None:
            self.process = subprocess.Popen([self.application_name, self.filename])
            #os.startfile(self.application_name + " -" + self.filename)

    def stop_application(self):
        if self.process is not None:
            self.process.kill()

    def kill_all_open(self):
        for p in psutil.process_iter():
            # check whether the process name matches
            if p.name() == "CallbackSample.exe":
                p.kill()


if __name__ == "__main__":
    leap_handler = LeapHandler("CallbackSample.exe", "main_test")
    leap_handler.start_application()

    poll = leap_handler.process.poll()
    print(poll)

    time.sleep(5)

    leap_handler.stop_application()
    time.sleep(5)
    poll = leap_handler.process.poll()
    print(poll)
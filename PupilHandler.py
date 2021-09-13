import psutil
import zmq
import logging

from PyQt5 import QtCore as Qtc


class PupilHandler(Qtc.QObject):

    def __init__(self):
        super().__init__()
        # This follows the network api protocol in the Pupil docs.
        self.ctx = zmq.Context()
        self.socket = zmq.Socket(self.ctx, zmq.REQ)
        self.is_calibrated = False
        self.pupil_capture_alive = False

    def start_connection(self):
        print("starting connection")
        res = self.socket.connect('tcp://127.0.0.1:50020')
        print(res)

    def get_status(self):
        # ensure that the pupil capture process is running
        if "pupil_capture.exe" in (p.name() for p in psutil.process_iter()):
            self.pupil_capture_alive = True
        else:
            self.pupil_capture_alive = False

    def start_recording(self, filename):

        # If the Pupil Capture application is not open then open a dialog asking the user to open up Pupil Capture.
        # Additionally the program will hang if it cannot communicate with the software.
        self.get_status()
        print("started recording")
        if self.pupil_capture_alive:
            try:
                self.socket.connect('tcp://127.0.0.1:50020')
                self.socket.send_string('R ' + filename)
                reply = self.socket.recv_string()
                print(reply)
            except:
                logging.error("Unable to start recording on Pupil Capture")

            else:
                logging.info("Start recording, reply: {}".format(reply))
        else:
            logging.error("Pupil Capture not alive")

    def stop_recording(self):

        # If the Pupil Capture application is not open then open a dialog asking the user to open up Pupil Capture.
        # Additionally the program will hang if it cannot communicate with the software.

        if self.pupil_capture_alive:
            try:
                self.socket.connect('tcp://127.0.0.1:50020')
                self.socket.send_string('r')
                reply = self.socket.recv_string()
            except:
                logging.error("Unable to stop recording on Pupil Capture")

            else:
                logging.info("Stop recording, reply: {}".format(reply))

if __name__ == "__main__":
    pupil_handler = PupilHandler()
    pupil_handler.start_recording("test")
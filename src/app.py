import sys

import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from pyzbar import pyzbar
from workstation import Artist, WorkStation


class WorkStationThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent, src=0):
        super().__init__(parent)
        self.capture = cv2.VideoCapture(src)
        width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH )
        height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT )
        self.workstation = WorkStation(width, height)
        self.artist = Artist()

    def convertToQImage(self, frame):
        # https://stackoverflow.com/a/55468544/6622587
        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        return QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

    def run(self):
        while True:
            ret, frame = self.capture.read()
            if ret:
                barcodes = pyzbar.decode(frame)
                task = self.workstation.process(barcodes)
                self.artist.draw_workstation(self.workstation, frame)

                pix = self.convertToQImage(frame)
                self.changePixmap.emit(pix)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'OpenCV to PyQT5'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(self.width, self.height)
        # create a label
        self.label = QLabel(self)
        self.label.resize(self.width, self.height)
        th = WorkStationThread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

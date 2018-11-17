import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()

        # self.left = 10
        # self.top = 10
        # self.width = 640
        # self.height = 480

        self.layout = QVBoxLayout()
        self.label = QLabel("No Data")

        self.layout.addWidget(self.label)
        self.setWindowTitle("Measurments Display")
        self.setLayout(self.layout)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

    def updateDisplay(self, measurments):
        
        self.layout = QVBoxLayout()
        self.label = QLabel("Humidity: " + str(measurments.getHumidity()) + "; Temperature: " + str(measurments.getTemperature())  + "; Quality: " + str(measurments.getAirQuality()) + "; Sound: " + str(measurments.getSound()))
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
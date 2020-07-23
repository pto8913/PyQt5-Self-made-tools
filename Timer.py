import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLCDNumber, QHBoxLayout
from PyQt5.QtCore import QTimer, QDateTime

class Timer(QWidget):
  def __init__(self):
    super().__init__()
    self.initUI()
  
  def initUI(self):
    timer = QTimer(self)
    timer.timeout.connect(self.updtTime)
    self.timeDisplay = QLCDNumber(self)
    self.timeDisplay.setSegmentStyle(QLCDNumber.Filled)
    self.timeDisplay.setDigitCount(8)
    self.updtTime()
    timer.start(1000)

    layout = QHBoxLayout()
    layout.addWidget(self.timeDisplay)

    self.setLayout(layout)

    self.setGeometry(300, 300, 500, 200)
    self.setWindowTitle('Timer')
    self.show()

  def updtTime(self):
    currentTime = QDateTime.currentDateTime().toString('hh:mm:ss')
    self.timeDisplay.display(currentTime)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = Timer()
  sys.exit(app.exec_())
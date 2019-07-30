import os
import sys
import time
from PyQt5.QtWidgets import (
  QApplication, QListWidget, QMessageBox, QPushButton, QWidget,
  QGridLayout, QVBoxLayout, QLineEdit, QFileDialog, QProgressDialog)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QFont

def debugOutput(out):
  sys.stdout.write(out + '\n')
  sys.stdout.flush()

class Notifier(QObject):
  notify = pyqtSignal()

class Thread(QThread):
  def __init__(self, notifier, name):
    super().__init__()
    
    self.notifier = notifier
    self.name = name
  
  def run(self):
    debugOutput('start thread :' + self.name)
    self.notifier.notify.emit()

class Main(QWidget):
  def __init__(self):
    super(Main, self).__init__()
    
    self.isRunning = False
    self.__initUI()
    
  def __initUI(self):
    startButton = QPushButton("start")
    startButton.clicked.connect(self.__onClicked)

    finishButton = QPushButton("finish")
    finishButton.clicked.connect(self.__finishClicked)
    
    layout = QVBoxLayout()
    layout.addWidget(startButton)
    layout.addWidget(finishButton)

    self.setLayout(layout)

  def __onClicked(self):
    self.notifier = Notifier()
    self.thread = Thread(self.notifier, 'test')
    self.notifier.moveToThread(self.thread)
    self.notifier.notify.connect(self.__sub, type = Qt.DirectConnection)
    self.thread.start()

  def __sub(self):
    self.isRunning = True
    while self.isRunning:
      time.sleep(2) 
      if not self.isRunning:
        break
      print("now running")

  def __finishClicked(self):
    self.isRunning = False
    print("fin")

def main():
  app = QApplication(sys.argv)
  font = QFont("Meiryo")
  app.setFont(font)
  w = Main()
  w.setWindowTitle("title")
  w.show()
  w.raise_()
  app.exec_()

if __name__ == '__main__':
  main()

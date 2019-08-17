""" ------------------------- main -------------------------------------"""
from PyQt5.QtWidgets import (
  QApplication, 
)

from PyQt5.QtGui import (
  QFont
)

import os
import sys

from myui import UI

class Main(UI):
  def __init__(self):
    super(Main, self).__init__()
    self.initUI()
    
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
 
""" -------------------------------- main -----------------------------""""

""" ------------------------------- sub --------------------------------"""
from PyQt5.QtWidgets import (
  QWidget,
  QPushButton, QGridLayout,
)

class UI(QWidget):
  def initUI(self):
    exitButton = QPushButton('Exit')
    exitButton.clicked.connect(self.clickedExit)

    buttonLayout = QGridLayout()
    buttonLayout.addWidget(exitButton, 1, 1)
    
    self.setLayout(buttonLayout)
  
  # clickedExitはmainのほうにあっても動く。
  def clickedExit(self):
    exit()
""" -------------------------------- sub -------------------------------"""

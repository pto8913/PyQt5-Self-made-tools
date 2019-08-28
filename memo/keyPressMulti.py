from PyQt5.QtWidgets import (
  QApplication, QWidget, QVBoxLayout, QLabel
)

from PyQt5.QtCore import (
  Qt
)

from PyQt5.QtGui import (
  QFont
)

import sys

class Main(QWidget):
  def __init__(self):
    super(Main, self).__init__()
    
    self.__initUI()
    
  def __initUI(self):
    self.label = QLabel("")
    layout = QVBoxLayout(self)
    layout.addWidget(self.label)
  
  def keyPressEvent(self, event):
    # modifier (修飾子)
    if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Return:
      self.label.setText("Press")
      return
    if event.key() == Qt.Key_Escape:
      exit()
  
  def keyReleaseEvent(self, event):
    self.label.setText("")

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

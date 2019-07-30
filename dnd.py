import os
import sys
from PyQt5.QtWidgets import (
  QApplication, QListWidget, QWidget, QVBoxLayout
)
from PyQt5.QtGui import QFont
from collections import deque

class Main(QWidget):
  def __init__(self):
    super(Main, self).__init__()

    self.setAcceptDrops(True)

    self.__FileList = QListWidget()
    self.__initUI()
    
  def __initUI(self):
    layout = QVBoxLayout()
    layout.addWidget(self.__FileList)

    self.setLayout(layout)

    self.setGeometry(1000, 500, 800, 500)

  def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()
  
  def dropEvent(self, event):
    urls = event.mimeData().urls()
  
    for url in urls:
      path = url.toLocalFile()
      tmp = path.split(".")
      if len(tmp) != 1:
        if tmp[1] == "xml":
          self.__FileList.addItem(os.path.basename(path))
      else:
        for roots, dirs, files in os.walk(tmp[0]):
          for f in files:
            if f.split(".")[1] == "xml":
              self.__FileList.addItem(os.path.basename(f))
  
          if len(dirs) != 0:
            self.__que = deque()
            for d in dirs:
              self.__que.append(d)
            self.__addDir()
  
  def __addDir(self):
    for roots, dirs, files in os.walk(self.__que.popleft()):
      for f in files:
        if f.split(".")[1] == "xml":
          self.__FileList.addItem(os.path.basename(f))
  
      if len(dirs) != 0:
        for d in dirs:
          self.__que.append(d)
        return self.__addDir()
  
    if len(self.__que) != 0:
      return self.__addDir()

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

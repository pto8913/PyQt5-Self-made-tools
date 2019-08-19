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
      tmp = path.split('.')
      if len(tmp) != 1:
        self.__FileList.addItem(basename(path))
      else:
        self.__addDir(tmp[0])
  
  def __addDir(self, item):
    for roots, dirs, files in os.walk(item):
      for f in files:
        self.__FileList.addItem(basename(f))

      if len(dirs) != 0:
        for d in dirs:
          self.__que.append(d)
        return self.__addDir(self.__que.popleft())

    try:
      if len(self.__que) != 0:
        return self.__addDir(self.__que.popleft())
    except:
      return
    
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

import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QAction
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.canvas = Canvas()
    self.initUI()
  
  def initUI(self):
    self.setCentralWidget(self.canvas)

    menubar = self.menuBar()

    exitAct = QAction('&Exit', self)
    exitAct.triggered.connect(self.close)

    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(exitAct)

    self.setGeometry(300, 300, 300, 200)
    self.setWindowTitle('Example')
    self.show()

class Canvas(QWidget):
  def __init__(self):
    super().__init__()
    self.px = None
    self.py = None
    self.points = []
    self.psets = []

  def mousePressEvent(self, event):
    self.points.append(event.pos())
    self.update()
  
  def mouseMoveEvent(self, event):
    self.points.append(event.pos())
    self.update()

  def mouseReleaseEvent(self, event):
    self.pressed = False
    self.psets.append(self.points)
    self.points = []
    self.update()

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.setPen(Qt.NoPen)
    painter.setBrush(Qt.white)
    painter.drawRect(self.rect())
    painter.setPen(Qt.black)

    for point in self.psets:
      painter.drawPolyline(*point)

    if self.points:
      painter.drawPolyline(*self.points)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MainWindow()
  sys.exit(app.exec_())

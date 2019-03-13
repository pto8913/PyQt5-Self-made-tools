import sys
from PyQt5.QtCore import Qt, QRect, QPoint, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QBrush, QColor, QScreen
from PyQt5.QtWidgets import (
  QWidget, QApplication, QMainWindow, QPushButton, QFileDialog
)
import copy
from pathlib import Path

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.initUI()
    self.ex = Snip()
  
  def initUI(self):
    startButton = QPushButton("Start", self)
    startButton.move(50, 50)
    startButton.clicked.connect(self.clickedStartButton)

    self.setGeometry(300, 300, 250, 100)
    self.setWindowTitle('board capture')
    self.show()

  def clickedStartButton(self):
    self.ex.showFullScreen()

class Snip(QWidget):
  endpos = QPoint(0, 0)
  stpos = QPoint(0, 0)
  def __init__(self):
    super().__init__()
    screen = QApplication.primaryScreen()
    self.originalPixmap = screen.grabWindow(
      QApplication.desktop().winId()
    )
  
  def paintEvent(self, event):
    painter = QPainter()
    painter.begin(self)
    painter.setPen(Qt.NoPen)

    rectSize = QApplication.desktop().screenGeometry()
    painter.drawPixmap(rectSize, self.originalPixmap)

    painterPath = QPainterPath()
    painterPath.addRect(QRectF(rectSize))
    painterPath.addRoundedRect(QRectF(self.stpos, self.endpos), 0, 0)

    painter.setBrush(QBrush(QColor(0, 0, 100, 100)))
    painter.drawPath(painterPath)

    painter.end()

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()

  def mouseMoveEvent(self, event):
    self.endpos = event.pos()
    self.repaint()

  def mousePressEvent(self, event):
    self.stpos = event.pos()

  def mouseReleaseEvent(self, event):
    self.endpos = event.pos()
    self.screenShot()

  def screenShot(self):
    pmap = self.originalPixmap.copy(QRect(self.stpos, self.endpos))
    filename, _ = QFileDialog.getSaveFileName(self)
    if len(filename) == 0:
      return
    filename = str(Path(filename).with_suffix(".png"))
    pmap.save(filename)
    self.close()
    return MainWindow()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MainWindow()
  sys.exit(app.exec_())
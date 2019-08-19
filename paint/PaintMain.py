import sys
from PyQt5.QtWidgets import (
  QApplication, QAction, QWidget, 
  QFileDialog, QColorDialog, QInputDialog
)
from PyQt5.QtGui import QPainter, QImage, QPen, qRgb
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QDir
from collections import deque

from PaintUI import MainUI

class MainWindow(MainUI):
  def __init__(self):
    super(MainWindow, self).__init__()
    self.canvas = Canvas()
    self.setCentralWidget(self.canvas)
    self.initUI()

  def selectColor(self):
    newColor = QColorDialog.getColor(self.canvas.penColor())
    self.canvas.setPenColor(newColor)

  def selectWidth(self):
    newWidth, ok = QInputDialog.getInt(
      self, "select",
      "select pen width: ", self.canvas.penWidth(), 1, 100, 1
    )
    if ok:
      self.canvas.setPenWidth(newWidth)

  def openFile(self):
    fileName, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
    if fileName:
      self.canvas.openImage(fileName)

  def saveFile(self):
    path = QDir.currentPath()
    fileName, _ = QFileDialog.getSaveFileName(self, "Save as", path)
    if fileName:
      return self.canvas.saveImage(fileName)
    return False

class Canvas(QWidget):
  def __init__(self, parent = None):
    super(Canvas, self).__init__(parent)

    self.myPenWidth = 2
    self.myPenColor = Qt.black
    self.image = QImage()
    self.check = False
    self.back = deque(maxlen = 10)
    self.next = deque(maxlen = 10)
    

  def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.back.append(self.resizeImage(self.image, self.image.size()))
      self.lastPos = event.pos()
      self.check = True
    
  def mouseMoveEvent(self, event):
    if event.buttons() and Qt.LeftButton and self.check:
      self.drawLine(event.pos())

  def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton and self.check:
      self.drawLine(event.pos())
      self.check = False

  def drawLine(self, endPos):
    painter = QPainter(self.image)
    painter.setPen(
      QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    )
    painter.drawLine(self.lastPos, endPos)
    self.update()
    self.lastPos = QPoint(endPos)

  def paintEvent(self, event):
    painter = QPainter(self)
    rect = event.rect()
    painter.drawImage(rect, self.image, rect)

  def resizeEvent(self, event):
    if self.image.width() < self.width() or self.image.height() < self.height():
      changeWidth = max(self.width(), self.image.width())
      changeHeight = max(self.height(), self.image.height())
      self.image = self.resizeImage(self.image, QSize(changeWidth, changeHeight))
      self.update()

  def resizeImage(self, image, newSize):
    changeImage = QImage(newSize, QImage.Format_RGB32)
    changeImage.fill(qRgb(255, 255, 255))
    painter = QPainter(changeImage)
    painter.drawImage(QPoint(0, 0), image)
    return changeImage

  def saveImage(self, filename):
    if self.image.save(filename):
      return True
    else:
      return False

  def openImage(self, filename):
    image = QImage()
    if not image.load(filename):
      return False

    self.image = image
    self.update()
    return True

  def penColor(self):
    return self.myPenColor

  def penWidth(self):
    return self.myPenWidth

  def setPenColor(self, newColor):
    self.myPenColor = newColor

  def setPenWidth(self, newWidth):
    self.myPenWidth = newWidth

  def resetImage(self):
    self.image.fill(qRgb(255, 255, 255))
    self.update()

  def backImage(self):
    if self.back:
      back_ = self.back.pop()
      self.next.append(back_)
      self.image = QImage(back_)
      self.update()

  def nextImage(self):
    if self.next:
      next_ = self.next.pop()
      self.back.append(next_)
      self.image = QImage(next_)
      self.update()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MainWindow()
  sys.exit(app.exec_())
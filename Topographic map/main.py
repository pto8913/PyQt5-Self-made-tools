import os
import sys
import json
import numpy as np
from PIL import Image
import matplotlib.cm as cmap
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
  QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
  QGridLayout, QListWidget, QLineEdit, QApplication
)
from PyQt5.QtGui import QPixmap, QImage

root = os.path.dirname(os.path.abspath(sys.argv[0]))

class Main(QWidget):
  global root
  def __init__(self, parent = None):
    super(Main, self).__init__(parent)
    
    self.fileList = QListWidget()
    self.setFileList()
    self.dirName = self.fileList.item(0).text()
    self.fileList.itemSelectionChanged.connect(self.showDir)

    latLabel = QLabel("lat : ")
    self.latEdit = QLineEdit()

    lonLabel = QLabel("lon : ")
    self.lonEdit = QLineEdit()

    editLayout = QGridLayout()
    editLayout.addWidget(latLabel, 0, 0)
    editLayout.addWidget(self.latEdit, 0, 1)
    editLayout.addWidget(lonLabel, 1, 0)
    editLayout.addWidget(self.lonEdit, 1, 1)

    startButton = QPushButton("Start")
    startButton.clicked.connect(self.clickedStart)
    
    exitButton = QPushButton("Exit")
    exitButton.clicked.connect(self.clickedExit)
    
    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(startButton)
    buttonLayout.addWidget(exitButton)

    inputLayout = QVBoxLayout()
    inputLayout.addWidget(self.fileList)
    inputLayout.addLayout(editLayout)
    inputLayout.addLayout(buttonLayout)

    self.canvas = QLabel()
    self.canvas.setScaledContents(True)

    entireLayout = QHBoxLayout()
    entireLayout.addLayout(inputLayout)
    entireLayout.addWidget(self.canvas)

    self.setLayout(entireLayout)

    self.setGeometry(300, 300, 300, 200)
    self.setWindowTitle("Main")

  def clickedStart(self):
    self.createTopographicImage()

  def setParam(self, lat, lon):
    self.latEdit.setText(lat)
    self.lonEdit.setText(lon)

  def clickedExit(self):
    sys.exit()

  def setFileList(self):
    for _, dirs, _ in os.walk(root):
      for d in dirs:
        self.fileList.addItem(os.path.basename(d))

  def showDir(self):
    self.showDirectory = ShowDir(self)
    self.showDirectory.widget.show()

  def filename(self, lat, lon):
    lat_a = lat / (2/ 3)
    lon_b = (lon - int(lon)) / (1/ 8)
    lat_b = (lat_a - int(lat_a)) / (1/ 8)
    lat_c = (lat_b * 10) % 10
    lon_c = (lon_b * 10) % 10
    return "{}{}".format(int(lat_c), int(lon_c))

  def elev(self, lat, lon):
    path = self.filename(lat, lon)
    elevs = np.full((225 * 150, ), np.nan)
    try:
      data = json.load(open(root + "/" + self.dirName + "/" + self.dirName + "_json/" + path + ".json", "r"))
      sp, raw = data["startPoint"], data["elevations"]
      elevs[sp: len(raw) + sp] = raw
    except:
      elevs = np.full((225 * 150, ), np.nan)
    elevs = elevs.reshape((150, 225))
    elevs = np.flipud(elevs)
    return elevs

  def createTopographicImage(self):
    lat, lon = float(self.latEdit.text()), float(self.lonEdit.text())
    elevs = self.elev(lat, lon)
    elevs[np.isnan(elevs)] = -9999.0

    fig, ax = plt.subplots()
    elevs = np.flipud(elevs)
    ls = LightSource(azdeg = 180, altdeg = 65)
    color = ls.shade(elevs, cmap.rainbow)
    cs = ax.imshow(elevs, cmap.rainbow)
    ax.imshow(color)

    make_axes = make_axes_locatable(ax)
    cax = make_axes.append_axes("right", size = "2%", pad = 0.05)
    fig.colorbar(cs, cax)

    ax.set_xticks([])
    ax.set_yticks([])
    fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    
    canvas = FigureCanvas(fig)
    canvas.draw()

    w, h = canvas.get_width_height()
    image = QImage(
      canvas.buffer_rgba(), w, h, QImage.Format_ARGB32
    )
    self.canvas.setPixmap(QPixmap(image))

class ShowDir:
  global root
  def __init__(self, parent = None):
    self.widget = QWidget()
    self.parent = parent
    self.main = Main()
    self.path = "/" + self.main.dirName + "/"

    self.fileList = QListWidget()
    self.setFileList()
    self.fileName = self.fileList.item(0).text()
    self.fileList.itemSelectionChanged.connect(self.changedSelectItem)

    okButton = QPushButton("Ok")
    okButton.clicked.connect(self.clickedOk)

    selectLayout = QVBoxLayout()
    selectLayout.addWidget(self.fileList)
    selectLayout.addWidget(okButton)

    self.widget.setLayout(selectLayout)

  def changedSelectItem(self):
    self.fileName = self.fileList.selectedItems()[0].text()
    with open(root + self.path + self.fileName, "r") as f:
      lat, lon = f.readline().split(",")
    self.parent.setParam(lat, lon)

  def clickedOk(self):
    self.widget.close()

  def show(self):
    self.widget.exec_()

  def setFileList(self):   
    for _, _, files in os.walk(root + self.path):
      for f in files:
        self.fileList.addItem(os.path.basename(f))
  
if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = Main()
  ex.show()
  sys.exit(app.exec_())

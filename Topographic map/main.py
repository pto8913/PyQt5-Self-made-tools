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

class LayoutClass(QWidget):
  global root
  def __init__(self):
    super().__init__()

    self.fileList = QListWidget()
    self.initUI()
  
  def initUI(self):
    self.setFileList()
    self.fileName = self.fileList.item(0).text()
    self.dirName = "/" + self.fileList.item(0).text()
    self.fileList.itemSelectionChanged.connect(self.changedSelectItem)

    self.view = QLabel()
    self.view.setScaledContents(True)

    latLabel = QLabel("lat(緯度): ")
    self.latEdit = QLineEdit(self)

    lonLabel = QLabel("lon(経度): ")
    self.lonEdit = QLineEdit(self)

    grid = QGridLayout()
    grid.addWidget(latLabel, 0, 0)
    grid.addWidget(self.latEdit, 0, 1)
    grid.addWidget(lonLabel, 1, 0)
    grid.addWidget(self.lonEdit, 1, 1)

    startButton = QPushButton("Start", self)
    startButton.clicked.connect(self.clickedStart)

    exitButton = QPushButton("Exit", self)
    exitButton.clicked.connect(self.clickedExit)

    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(startButton)
    buttonLayout.addWidget(exitButton)

    inputLayout = QVBoxLayout()
    inputLayout.addWidget(self.fileList)
    inputLayout.addLayout(grid)
    inputLayout.addLayout(buttonLayout)

    entireLayout = QHBoxLayout()
    entireLayout.addLayout(inputLayout)
    entireLayout.addWidget(self.view)

    self.setLayout(entireLayout)

    self.setGeometry(0, 0, 1000, 600)
    self.setWindowTitle("Main")
    self.show()

  def clickedStart(self):
    self.createTopographicImage()

  def clickedExit(self):
    sys.exit()

  def setFileList(self):
    for _, dirs, _ in os.walk(root):
      for d in dirs:
        self.fileList.addItem(os.path.basename(d))

  def changedSelectItem(self):
    self.dirName = "/" + self.fileList.selectedItems()[0].text()
    self.fileName = self.fileList.selectedItems()[0].text()
    self.showdir = showDir()
    self.showdir
    self.close()

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
      data = json.load(open(root + self.dirName + "/" + self.dirName + "_json/" + path + ".json", "r"))
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

    canvas = FigureCanvas(fig)
    canvas.draw()

    w, h = canvas.get_width_height()
    image = QImage(
      canvas.buffer_rgba(), w, h, QImage.Format_ARGB32
    )
    self.view.setPixmap(QPixmap(image))

class showDir(QWidget):
  global root
  def __init__(self, parent = None):
    super(showDir, self).__init__(parent)

    self.fileLayout = LayoutClass()
    self.fileList = QListWidget()
    self.initUI()
  
  def initUI(self):
    self.setFileList()
    self.fileName = self.fileList.item(0).text()
    self.fileList.itemSelectionChanged.connect(self.fileListChanged)

    hbox = QHBoxLayout()
    hbox.addWidget(self.fileList)

    self.setLayout(hbox)

    self.setGeometry(1050, 100, 300, 200)
    self.setWindowTitle("Show Directory")
    self.show()

  def setFileList(self):
    dirName = self.fileLayout.dirName + "/"
    for _, _, files in os.walk(root + dirName):
      for f in files:
        self.fileList.addItem(os.path.basename(f))

  def fileListChanged(self):
    self.fileName = self.fileList.selectedItems()[0].text()
    path = self.fileLayout.dirName + "/" + self.fileName
    with open(root + path, "r") as f:
      lat, lon = f.readline().split(",")
    self.fileLayout.latEdit.setText(lat)
    self.fileLayout.lonEdit.setText(lon)
    self.fileLayout.show()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = LayoutClass()
  sys.exit(app.exec_())

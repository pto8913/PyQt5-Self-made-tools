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
  QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSplitter, QAction, QMessageBox,
  QGridLayout, QListWidget, QLineEdit, QApplication, QMainWindow, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

root = os.path.dirname(os.path.abspath(sys.argv[0]))

class GenerateTerrainImage(QWidget):
  global root
  def __init__(self, parent = None):
    super(GenerateTerrainImage, self).__init__(parent)
    
    self.dirList = QListWidget()
    self.fileList = QListWidget()

    self.setDirList()
    self.fileName = ""
    self.dirName = self.dirList.item(0).text()
    self.path = "/" + self.dirName + "/"
    self.dirList.itemSelectionChanged.connect(self.selectDir)
    self.fileList.itemSelectionChanged.connect(self.selectFile)

    latLabel = QLabel("lat(緯度): ")
    self.latEdit = QLineEdit()

    lonLabel = QLabel("lon(経度): ")
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
    inputLayout.addWidget(self.dirList)
    inputLayout.addLayout(editLayout)
    inputLayout.addLayout(buttonLayout)

    inputWidget = QWidget()
    inputWidget.setLayout(inputLayout)

    self.canvas = QLabel(u" ここに地形図が表示されます ")
    self.canvas.setScaledContents(True)

    saveButton = QPushButton("Save Figure")
    saveButton.clicked.connect(self.clickedSave)

    figureLayout = QVBoxLayout()
    figureLayout.addWidget(self.canvas)
    figureLayout.addWidget(saveButton)

    figureWidget = QWidget()
    figureWidget.setLayout(figureLayout)

    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(inputWidget)
    splitter.addWidget(figureWidget)
    splitter.setStretchFactor(1, 1)

    entireLayout = QHBoxLayout()
    entireLayout.addWidget(splitter)
    entireLayout.addWidget(self.fileList)

    self.setLayout(entireLayout)

  def clickedSave(self):
    try:
      if self.image:
        fileName, _ = QFileDialog.getSaveFileName(self, "Save")
        self.image.save(fileName)
    except:
      QMessageBox.information(self, "Not Exist Image Error", "Can't save not exist Image", QMessageBox.Ok)

  def clickedStart(self):
    self.createTopographicImage()

  def setParam(self, lat, lon):
    self.latEdit.setText(lat)
    self.lonEdit.setText(lon)

  def clickedExit(self):
    sys.exit()

  def setDirList(self):
    for _, dirs, _ in os.walk(root):
      for d in dirs:
        if "_json" not in d:
          self.dirList.addItem(os.path.basename(d))

  def selectDir(self):
    self.dirName = self.dirList.selectedItems()[0].text()
    for _, _, files in os.walk(root + self.path):
      for f in files:
        _, ext = f.split(".")
        if ext == "txt":
          self.fileList.addItem(os.path.basename(f))

  def selectFile(self):
    self.fileName = self.fileList.selectedItems()[0].text()
    with open(root + self.path + self.fileName, "r") as f:
      lat, lon = f.readline().split(",")
    self.setParam(lat, lon)

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
    try:
      lat, lon = float(self.latEdit.text()), float(self.lonEdit.text())
    except:
      QMessageBox.information(self, "None file Error", "Can't create map. <br> Please Press lat and lon.", QMessageBox.Ok)
      return
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
    self.image = QImage(
      canvas.buffer_rgba(), w, h, QImage.Format_ARGB32
    )
    self.canvas.setPixmap(QPixmap(self.image))
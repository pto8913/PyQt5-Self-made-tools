import sys
from PyQt5.QtWidgets import (
  QApplication, QLabel, QLineEdit, QBoxLayout, QMainWindow,
  QGridLayout, QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
  QTextEdit, QAction, QTextEdit
)
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
import json
from mpl_toolkits.axes_grid1 import make_axes_locatable

class Map(QMainWindow):
  def __init__(self):
    super().__init__()
    self.initUI()
  
  def initUI(self):
    self.Input = Input(self)
    self.setCentralWidget(self.Input)

    exitAct = QAction('&Exit', self)
    exitAct.setShortcut('Ctrl+Q')
    exitAct.triggered.connect(self.close)

    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(exitAct)

    self.setGeometry(300, 300, 300, 200)
    self.setWindowTitle('Example')
    self.show()

class Input(QWidget):
  def __init__(self, parent):
    super().__init__(parent)
    self.initInput()
  
  def initInput(self):
    lat = QLabel("lat :")
    lon = QLabel("lon :")
    self.startButton = QPushButton("start")
    self.quitButton = QPushButton("quit")

    self.startButton.clicked.connect(self.startClicked)
    self.quitButton.clicked.connect(self.quitClicked)

    self.latEdit = QLineEdit(self)
    self.lonEdit = QLineEdit(self)

    vbox = QVBoxLayout()
    hbox = QHBoxLayout()

    hbox.addWidget(lat)
    hbox.addWidget(self.latEdit)
    vbox.addLayout(hbox)

    hbox = QHBoxLayout()
    hbox.addWidget(lon)
    hbox.addWidget(self.lonEdit)
    vbox.addLayout(hbox)

    hbox = QHBoxLayout()
    hbox.addWidget(self.startButton)
    hbox.addWidget(self.quitButton)
    vbox.addLayout(hbox)

    self.setLayout(vbox)

    self.setGeometry(300, 300, 300, 200)
    self.setWindowTitle('Topographic map')
    self.show()

  def filename(self, lat, lon):
    lat_a = lat / (2/ 3)
    lon_b = (lon - int(lon)) / (1/ 8)
    lat_b = (lat_a - int(lat_a)) / (1/ 8)
    lat_c = (lat_b * 10) % 10
    lon_c = (lon_b * 10) % 10
    return "{}{}".format(int(lat_c), int(lon_c))
  
  def elev(self, lat, lon):
    path = "path"
    name = self.filename(lat, lon)
    elevs = np.full((225 * 150, ), np.nan)
    try:
      data = json.load(open(path + name + ".json", "r"))
      sp = data["startPoint"] 
      raw = data["elevations"]
      elevs[sp: len(raw) + sp] = raw
    except:
      pass
    elevs = elevs.reshape((150, 225))
    elevs = np.flipud(elevs)
    return elevs

  def quitClicked(self):
    self.close()

  def startClicked(self):
    lat = float(self.latEdit.text())
    lon = float(self.lonEdit.text())

    calc_lon = 1/ 8/ 10
    calc_lat = 2/ 3/ 8/ 10
    elevs1 = self.elev(lat, lon)
    elevs2 = self.elev(lat, lon - calc_lon)
    elevs3 = self.elev(lat, lon + calc_lon)
    elevs4 = self.elev(lat + calc_lat, lon - calc_lon)
    elevs5 = self.elev(lat + calc_lat, lon)
    elevs6 = self.elev(lat + calc_lat, lon + calc_lon)

    elevs = np.vstack((
      np.hstack((elevs2, elevs1, elevs3)),
      np.hstack((elevs4, elevs5, elevs6))
    ))

    elevs[np.isnan(elevs)] = np.nanmin(elevs)

    fig, ax = plt.subplots()
    elevs = np.flipud(elevs)
    ls = LightSource(azdeg = 180, altdeg = 65)
    color = ls.shade(elevs, cm.rainbow)
    cs = ax.imshow(elevs, cm.rainbow)
    ax.imshow(color)

    make_axes = make_axes_locatable(ax)
    cax = make_axes.append_axes("right", size = "2%", pad = 0.05)

    fig.colorbar(cs, cax)

    ax.set_xticks([])
    ax.set_yticks([])

    plt.show()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = Map()
  sys.exit(app.exec_())

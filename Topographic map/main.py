import os
import sys
import json
import warnings
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

# プログラムが存在するディレクトリ名だよ
root = os.path.dirname(os.path.abspath(sys.argv[0]))

# メインウィンドウだよ
class MainWindow(QMainWindow):
  def __init__(self):
    super(MainWindow, self).__init__()

    # Mainクラスを呼び出すよ。
    self.main = Main()
    # メインウィンドウに配置してあげるよ
    self.setCentralWidget(self.main)
    self.initUI()

  def initUI(self):
    # メニューバーを作るよ
    menubar = self.menuBar()
    # セーブアクションだよ
    saveAct = QAction('&Save', self)
    # ショートカットキーを設定するよ
    saveAct.setShortcut('Ctrl+S')
    # メニューをクリックするかショートカットキーを押すと動くよ
    saveAct.triggered.connect(self.main.clickedSave)

    # アプリを終了するアクションだよ
    exitAct = QAction('&Exit', self)
    # ショートカットキーを設定するよ
    exitAct.setShortcut('Ctrl+Q')
    # メニューをクリックするかショートカットキーを押すと動くよ
    exitAct.triggered.connect(self.main.clickedExit)

    # ファイルメニューを作るよ
    fileMenu = menubar.addMenu('&File')
    # メニューにアクションを追加するよ
    fileMenu.addAction(saveAct)
    fileMenu.addAction(exitAct)

    # ヘルプアクションだよ
    helpAct = QAction('Help', self)
    # メニューをクリックすると動くよ
    helpAct.triggered.connect(self.clickedHelp)

    # ヘルプメニューを作るよ
    helpMenu = menubar.addMenu('&Help')
    # メニューにアクションを追加するよ
    helpMenu.addAction(helpAct)
    
    # ウィンドウの大きさを決めるよ
    self.setGeometry(0, 0, 800, 400)
    # ウィンドウのタイトルを決めるよ
    self.setWindowTitle("MainWindow")
    # 表示するよ
    self.show()

  def clickedHelp(self):
    # ヘルプメッセージを表示するよ
    # 英語がいっぱいで難しいお；；
    QMessageBox.information(
      self,
      "Help", 
      "This is Help <br> lat is latitude, lon is longitude. <br> \
      Enter lat and lon by yourself or select from file list <br> \
      if lat or lon is blank, you can't show map. \
      if you want to save figure press Ctrl+S or click Save Figure, <br> \
      but Be careful Not exist figure can't save.",
      # おーるおっけーだよー＾＾
      QMessageBox.Ok
    )

class Main(QWidget):
  # グローバルなルートくんだよ。ハローハロー＾＾
  global root
  def __init__(self, parent = None):
    super(Main, self).__init__(parent)
    
    # ディレクトリ名を表示するためのウィジェットだよ
    self.DirList = QListWidget()
    # ウィジェットに要素を入れていくよ。ここではディレクトリ名のことだよ
    self.setDirList()

    # ディレクトリ名だよ
    self.DirName = ""
    # ウィジェットの中の要素をクリックしたときに処理が動くよ
    self.DirList.itemSelectionChanged.connect(self.selectDir)
    
    # ファイル名を表示するためのウィジェットだよ
    self.FileList = QListWidget()
    # ファイル名だよ
    self.FileName = ""
    # ウィジェットの中の要素をクリックしたときに処理が動くよ
    self.FileList.itemSelectionChanged.connect(self.selectFile)

    # ラベルだよ
    LatLabel = QLabel("lat(緯度): ")
    # 緯度を入力するところだよ
    self.LatEdit = QLineEdit()
    # ラベルだよ
    LonLabel = QLabel("lon(経度): ")
    # 経度を入力するところだよ
    self.LonEdit = QLineEdit()
    
    # ラベルとエディタを配置するよ
    editLayout = QGridLayout()
    editLayout.addWidget(LatLabel, 0, 0)
    editLayout.addWidget(self.LatEdit, 0, 1)
    editLayout.addWidget(LonLabel, 1, 0)
    editLayout.addWidget(self.LonEdit, 1, 1)

    # 地形図を表示するときに使うボタンだよ
    startButton = QPushButton("Start")
    # クリックされたら動くよ
    startButton.clicked.connect(self.clickedStart)

    # アプリを閉じるときに使うボタンだよ。Ctrl+Qでショートカットキーを作ったね。
    exitButton = QPushButton("Exit")
    # クリックされたら動くよ
    exitButton.clicked.connect(self.clickedExit)
    
    # ボタンを配置するよ
    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(startButton)
    buttonLayout.addWidget(exitButton)

    # エディタレイアウトとボタンレイアウトとディレクトリリストを配置するよ
    inputLayout = QVBoxLayout()
    inputLayout.addWidget(self.DirList)
    inputLayout.addLayout(editLayout)
    inputLayout.addLayout(buttonLayout)

    # 後でウィジェットの大きさ変えられるようにするためにウィジェットにするよ
    inputWidget = QWidget()
    # ウィジェットにレイアウトを配置するよ
    inputWidget.setLayout(inputLayout)

    # 地形図を表示するラベルだよ
    self.Canvas = QLabel(u" ここに地形図が表示されます ")
    # ウィンドウの大きさを変えたとき画像を自動的に伸縮するよ
    self.Canvas.setScaledContents(True)

    # 保存するときにクリックするボタンだよ。Ctrl+Sにショートカットキーを作ったね。
    saveButton = QPushButton("Save Figure")
    # クリックしたときに処理が動くよ
    saveButton.clicked.connect(self.clickedSave)

    # ラベルとボタンを配置するよ
    figureLayout = QVBoxLayout()
    figureLayout.addWidget(self.Canvas)
    figureLayout.addWidget(saveButton)

    # 後でウィジェットの大きさ変えられるようにするためにウィジェットにするよ
    figureWidget = QWidget()
    # ウィジェットにレイアウトを配置するよ
    figureWidget.setLayout(figureLayout)

    # ウィジェットの大きさを変えられるようにするよ
    splitter = QSplitter(Qt.Horizontal)
    splitter.addWidget(inputWidget)
    splitter.addWidget(figureWidget)
    splitter.setStretchFactor(1, 1)

    # 全体のレイアウトだよ
    entireLayout = QHBoxLayout()
    entireLayout.addWidget(splitter)
    entireLayout.addWidget(self.FileList)

    # レイアウトをMainクラスに配置するよ
    self.setLayout(entireLayout)

  def selectFile(self):
    try:
      # ファイルリストのファイルが選択されたら選択されたファイルの名前を保存しておくよ
      self.FileName = self.FileList.selectedItems()[0].text()
      # ファイルが存在するディレクトリだよ
      self.OpenFileRoot = root + self.path + self.DirName + "_json_n_txt/"
      # ファイルを開いて緯度経度を受け取るよ
      with open(self.OpenFileRoot + self.FileName, "r") as f:
        lat, lon = f.readline().split(",")
      # 緯度経度をエディタにセットするよ
      self.setParam(lat, lon)
    except:
      # ファイルがなかったら何も処理しないよ
      return

  def setDirList(self):
    # ディレクトリ名をディレクトリリストに追加するよ
    for _, dirs, _ in os.walk(root):
      for d in dirs:
        if "_json" not in d:
          self.DirList.addItem(os.path.basename(d))

  def selectDir(self):
    # ディレクトリ名をクリックしたら選択したディレクトリ名を保存しておくよ
    self.DirName = self.DirList.selectedItems()[0].text()
    # / をいっぱい書くのが面倒だからここで適当に保存しておくよ
    self.path = "/" + self.DirName + "/"
    # ファイルリストに要素が入ってるなら要素を全部削除するよ
    if self.FileList:
      self.FileList.clear()
    # ファイル名をファイルリストに追加するよ
    for _, _, files in os.walk(root + self.path):
      for f in files:
        _, ext = f.split(".")
        # txtファイル以外のファイルは表示しないようにしているよ
        if ext == "txt":
          self.FileList.addItem(os.path.basename(f))

  def calcname(self, lat_lon, mold):
    # 緯度経度からファイル名を求めるよ
    a = (lat_lon % 100) / mold
    b = (a - int(a)) / (1/ 8)
    c = (b / (1/10)) % 10
    return int(c)

  def filename(self, lat, lon):
    calclat = self.calcname(lat, 2/3)
    calclon = self.calcname(lon, 1)
    return "{}{}".format(calclat, calclon)

  def elev(self, lat, lon):
    filename = self.filename(lat, lon)
    # 225*150の大きさの配列を作ってnanで埋めておくよ
    elevs = np.full((225 * 150, ), np.nan)
    try:
      # 標高データをjsonファイルから読み込むよ
      with open(self.OpenFileRoot + filename + ".json", "r") as f:
        data = json.load(f)
        sp, raw = data["startPoint"], data["elevations"]
        elevs[sp: len(raw) + sp] = raw
      # ファイルを閉じないといっぱい怒られるよ
      f.close()
    except:
      # ファイルが存在しないなら何もしないよ
      pass
    # 配列の大きさを150*225の大きさに変形するよ
    elevs = elevs.reshape((150, 225))
    # 配列を反転するよ
    elevs = np.flipud(elevs)
    return elevs

  def createTopographicImage(self):
    try:
      # 緯度、経度をエディタから受け取るよ
      lat, lon = float(self.LatEdit.text()), float(self.LonEdit.text())
    except:
      # 緯度経度が入力されていなかったらエラーメッセージを表示するよ
      QMessageBox.information(self, "None file Error", "Can't create map. <br> Please Press lat and lon.", QMessageBox.Ok)
      return
    # 大きな画像いやだって人は下のコメントアウト外してね
    #elevs = self.elev(lat, lon)
    # ここの端の時の処理思いつかなかったよ；；
    calc_lon = 0.013
    calc_lat = 0.00833333333
    elevs1 = self.elev(lat, lon)
    elevs2 = self.elev(lat, lon + calc_lon)
    elevs3 = self.elev(lat + calc_lat, lon)
    elevs4 = self.elev(lat + calc_lat, lon + calc_lon)
    elevs = np.vstack((
        np.hstack((elevs1, elevs2)),
        np.hstack((elevs3, elevs4))
    ))
    # 配列の要素が全部nanだったときに怒られちゃったからここで例外処理をするよ
    warnings.simplefilter('error')
    try:
      # 配列の中のnanを同じ配列の中のnan以外で最小のものにするよ
      elevs[np.isnan(elevs)] = np.nanmin(elevs)
    except RuntimeWarning:
      # 配列の要素が全部nanだったときこっちの処理が動くよ
      elevs[np.isnan(elevs)] = -9999.0

    # 図を表示するときに使うよ
    fig, ax = plt.subplots()
    # 配列の反転だよ
    elevs = np.flipud(elevs)
    # azdeg: 光源の方位 0 ~ 360 altdeg: 光源の高度 0 ~ 90
    # 配列に色や影を追加するよ
    ls = LightSource(azdeg = 180, altdeg = 65)
    # カラーマップのデータを配列と組み合わせるよ
    color = ls.shade(elevs, cmap.rainbow)
    cs = ax.imshow(elevs, cmap.rainbow)
    ax.imshow(color)

    # 新しいラベルを作るよ
    make_axes = make_axes_locatable(ax)
    # 新しく作ったラベルの設定左から位置、ラベルの大きさ、パディングだよ
    cax = make_axes.append_axes("right", size = "2%", pad = 0.05)
    # 図に新しく作ったラベルを追加するよ
    fig.colorbar(cs, cax)

    # x軸y軸を消すよ
    ax.set_xticks([])
    ax.set_yticks([])

    # 画像の周りの余白をいじるよ
    fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
    
    # 画像をキャンバスに追加するよ
    canvas = FigureCanvas(fig)
    # キャンバスに描画するよ
    canvas.draw()

    # キャンバスの大きさを受け取るよ
    w, h = canvas.get_width_height()
    # キャンバスの画像をQImage型にするよ
    self.Image = QImage(
      canvas.buffer_rgba(), w, h, QImage.Format_ARGB32
    )
    # 地形図を表示するラベルに画像をセットするよ
    self.Canvas.setPixmap(QPixmap(self.Image))
  
  def clickedSave(self):
    try:
      # 保存するよ
      if self.Image:
        fileName, _ = QFileDialog.getSaveFileName(self, "Save")
        self.Image.save(fileName)
    except:
      # 画像が存在しなかったらメッセージが表示されるよ
      QMessageBox.information(self, "Not Exist Image Error", "Can't save not exist Image", QMessageBox.Ok)

  def clickedStart(self):
    # マップを表示するよ
    self.createTopographicImage()

  def setParam(self, lat, lon):
    # エディタに緯度経度をセットするよ
    self.LatEdit.setText(lat)
    self.LonEdit.setText(lon)

  def clickedExit(self):
    # アプリを終了するよ
    sys.exit()

if __name__ == '__main__':
  # 動け～
  app = QApplication(sys.argv)
  ex = MainWindow()
  sys.exit(app.exec_())

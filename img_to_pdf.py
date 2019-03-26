import os
import sys
import img2pdf
from PIL import Image 
from PyQt5.QtWidgets import (
  QWidget, QApplication, QListWidget, QPushButton, QGridLayout, QComboBox, QAction,
  QVBoxLayout, QFileDialog, QMessageBox, QInputDialog, QLineEdit, QMainWindow,
)
from PyQt5.QtCore import Qt

# プログラムが存在するディレクトリ名だよ
root = os.path.dirname(os.path.abspath(sys.argv[0]))
# ファイルの名前を受け取るときに使うよ。lambdaくんは優秀だね
basename = lambda x: os.path.basename(x)

# メインウィンドウだよ
class Main(QMainWindow):
  def __init__(self):
    super(Main, self).__init__()

    # Layoutクラスを呼び出すよ
    self.myLayout = Layout()
    # メインウィンドウに配置してあげるよ
    self.setCentralWidget(self.myLayout)
    self.initUI()
  
  def initUI(self):
    # メニューバーを作るよ
    menubar = self.menuBar()
    
    # セーブアクションだよ
    saveAct = QAction("Save", self)
    # ショートカットキーを設定するよ
    saveAct.setShortcut("Ctrl+S")
    # メニューをクリックするかショートカットキーを押すと動くよ
    saveAct.triggered.connect(self.myLayout.clickedSave)

    # アプリを終了するアクションだよ
    exitAct = QAction("Exit", self)
    # ショートカットキーを設定するよ
    exitAct.setShortcut("Ctrl+Q")
    # メニューをクリックするかショートカットキーを押すと動くよ
    exitAct.triggered.connect(self.myLayout.clickedExit)

    # ファイルを追加するアクションだよ
    openAct = QAction("Open", self)
    # ショートカットキーを設定するよ
    openAct.setShortcut("Ctrl+O")
    # メニューをクリックするかショートカットキーを押すと動くよ
    openAct.triggered.connect(self.myLayout.clickedAdd)

    # ファイルリストの中をリセットするよ
    resetAct = QAction("Reset", self)
    # メニューをクリックするかショートカットキーを押すと動くよ
    resetAct.triggered.connect(self.myLayout.clickedClear)

    # ファイルメニューを作るよ
    fileMenu = menubar.addMenu("&File")
    # メニューにアクションを追加するよ
    fileMenu.addAction(resetAct)
    fileMenu.addAction(saveAct)
    fileMenu.addAction(openAct)
    fileMenu.addAction(exitAct)

    # ウィンドウの大きさを決めるよ
    self.setGeometry(100, 100, 300, 400)
    # ウィンドウのタイトルを決めるよ
    self.setWindowTitle("img2pdf")

class Layout(QWidget):
  # グローバルなルートくんとベースネームくんだよ
  global root, basename
  def __init__(self, parent = None):
    super(Main, self).__init__(parent)
    
    # ドラッグアンドドロップを出来るようにするよ
    self.setAcceptDrops(True)
    # 画像ファイルのパスを入れる箱だよ
    self.ImagePathList = []
    # 選んでいるファイルの名前だよ。リストから消すときに使うよ
    self.SelectFileName = ""
    # 拡張子だよ。後でjpgに変わったりするよ
    self.Extension = ".png"
    # ファイル名を表示するためのウィジェットだよ
    self.FileList = QListWidget()
    self.initUI()

  def initUI(self):
    # ここでpngファイルかjpgファイルか選んでおこうね。
    selectFormat = QComboBox()
    selectFormat.addItem(".png")
    selectFormat.addItem(".jpg")
    # 選ばれたのは綾鷹だよ
    selectFormat.activated[str].connect(self.onActivated)

    # 保存するときに使うボタンだよ。
    saveButton = QPushButton("Save")
    # ボタンをクリックしたら動くよ
    saveButton.clicked.connect(self.clickedSave)

    # アプリを終了するボタンだよ
    exitButton = QPushButton("Exit")
    # ボタンをクリックしたら動くよ
    exitButton.clicked.connect(self.clickedExit)

    # ファイルを追加するボタンだよ
    addButton = QPushButton("Add Item")
    # ボタンをクリックしたら動くよ
    addButton.clicked.connect(self.clickedAdd)

    # ファイルを全部消すボタンだよ。僕もすべてを消すボタンを作りたいよ
    clearButton = QPushButton("Clear Item")
    # ボタンをクリックしたら動くよ
    clearButton.clicked.connect(self.clickedClear)

    # 選んでいるファイルをリストから消すよ
    deleteButton = QPushButton("Delete Item")
    # ボタンをクリックしたら動くよ
    deleteButton.clicked.connect(self.clickedDelete)

    # ファイル名で並び替えるよ
    sortButton = QPushButton("Sort Item")
    # ボタンをクリックしたら動くよ
    sortButton.clicked.connect(self.clickedSort)

    # ボタンを配置するよ
    buttonLayout = QGridLayout()
    buttonLayout.addWidget(saveButton, 0, 0)
    buttonLayout.addWidget(clearButton, 0, 1)
    buttonLayout.addWidget(exitButton, 0, 2)
    buttonLayout.addWidget(addButton, 1, 0)
    buttonLayout.addWidget(deleteButton, 1, 1)
    buttonLayout.addWidget(sortButton, 1, 2)

    # 全体のレイアウトだよ
    entireLayout = QVBoxLayout()
    entireLayout.addWidget(self.FileList)
    entireLayout.addWidget(selectFormat)
    entireLayout.addLayout(buttonLayout)

    # レイアウトをLayoutクラスに配置するよ
    self.setLayout(entireLayout)

  def onActivated(self, text):
    # コンボボックスで選ばれた拡張子に設定するよ
    self.Extension = text

  def dragEnterEvent(self, event):
    # ドラッグされたファイルにパスがあればTrue
    if event.mimeData().hasUrls():
      # 受け取るよ
      event.accept()
    else:
      # 無視するよ
      event.ignore()

  def dropEvent(self, event):
    # 受け取ったファイルのデータからパスを抜き出すよ
    urls = event.mimeData().urls()
    # ファイルが1つだけなら動くよ
    if len(urls) == 1:
      # リストに追加するよ
      self.setFileList(urls[0].toLocalFile())
      return
    # ファイルが1つ以上ならこっちが動くよ
    for url in urls:
      # パスの部分だけ抜き出すよ
      path = url.toLocalFile()
      # ファイルの名前だよ
      filename = basename(path)
      # ファイル名に選ばれた拡張子が入ってたらTrue
      if self.checkInExt(filename):
        # リストにファイル名を追加するよ
        self.FileList.addItem(filename)
        # ファイルのパスを追加するよ
        self.ImagePathList.append(path)

  def setFileList(self, urls):
    filename = basename(urls)
    if self.checkInExt(filename):
      self.FileList.addItem(filename)
      self.ImagePathList.append(urls)

  def clickedAdd(self):
    # ファイルを開くよ
    FileName, ok = QFileDialog.getOpenFileName(self, "Open", root)
    if FileName:
      filename = basename(FileName)
      if self.checkInExt(filename):
        self.FileList.addItem(filename)
        self.ImagePathList.append(FileName)
        return
    # キャンセルが押されたときのための処理だよ
    if not ok:
      return
    # ファイルの拡張子がpngかjpgじゃないと怒られちゃうよ
    QMessageBox.information(
      self, 
      "Unsupported File Format", 
      "You can select png or jpg <br>\
       If your file format is png or jpg, <br>\
       but you can't add file, your file format is Strange. <br>\
       Please confirm your file. \
      ", 
      QMessageBox.Ok
    )

  def clickedSave(self):
    # 入力フォームだよ。保存するpdfの名前を決められるよ
    filename, _ = QInputDialog.getText(
      self, 
      "Enter Filename", 
      "filename: ", 
      QLineEdit.Normal, 
      ""
    )
    try:
      path = root + "/" + filename + ".pdf"
      if os.path.exists(path):
        # ファイル名が存在していたら怒られるよ
        QMessageBox.information(
          self,
          "Filename Error",
          "This filename is already exists <br>\
           Please change.\
          ",
          QMessageBox.Ok
        )
        return self.clickedSave()
      # ファイルをpdfに変換して保存するよ。(ここだけあれば他の9割いらないよ)
      with open(path , "wb") as f:
        # ファイルのパスが入っている順番通りにpdfにしていくよ
        f.write(img2pdf.convert([f for f in self.ImagePathList]))
      f.close()
    except:
      # 手動でファイルの拡張子をpngとかjpgに変えているファイルの時に起こるよ
      # (多分。確認はしてない。)
      QMessageBox.information(
        self, 
        "WARNING", 
        "PLEASE CHECK YOUR FILE FORMAT <br>\
         THIS IS VERY VERY STRANGE SITUATION. <br>\
        ",
        QMessageBox.Ok
      )
  
  def checkInExt(self, filename):
    # 拡張子がファイル名に入っていたらTrue
    if self.Extension in filename:
      return True
    return False

  def keyPressEvent(self, event):
    # ESCキーが押されたら閉じるよ
    if event.key() == Qt.Key_Escape:
      self.clickedExit()

  def clickedExit(self):
    sys.exit()

  def clickedSort(self):
    # ソートだよ。lambdaくんは優秀だね。
    # ImagePathListにはパスが入っているんだよ。
    # だから、パスでソートするんじゃなくてファイルの名前でソートしているよ
    self.ImagePathList = sorted(self.ImagePathList, key =  lambda x: basename(x))
    # ファイルリストの中のソートだよ
    self.FileList.sortItems()

  def clickedClear(self):
    # ぜーーーーーーんぶリセット
    self.ImagePathList = []
    self.FileList.clear()

  def clickedDelete(self):
    try:
      # ファイルを一つだけ消したいときに使うよ
      # ファイルリストの中で選んでいるファイルの行を受け取るよ
      row = self.FileList.row(self.FileList.selectedItems()[0])
      # ファイルリストとパスの中から削除するよ
      self.ImagePathList.pop(row)
      self.FileList.takeItem(row)
    except:
      # 何も選んでいないと怒られるよ
      QMessageBox.information(
        self, 
        "No Item Error", 
        "Select delete item", 
        QMessageBox.Ok
      )

if __name__ == '__main__':
  # 動け～
  app = QApplication(sys.argv)
  ex = Main()
  ex.show()
  sys.exit(app.exec_())

import os
import sys
import time

import numpy as np
import sqlite3
from collections import deque

from PyQt5.QtWidgets import (
  QApplication, 
  QListWidget, QWidget, QMainWindow, QDockWidget,
  QLineEdit, QPushButton, QTextEdit, 
  QTreeView,
  QAction, QSizePolicy, 
  QMessageBox, QFileDialog, QProgressDialog, 
  QGridLayout, QVBoxLayout, QHBoxLayout,
)

from PyQt5.QtCore import (
  Qt, QObject, QThread, pyqtSignal, QMutex, QMutexLocker, QSize,
)
from PyQt5.QtGui import (
  QFont, QStandardItemModel, QStandardItem, 
)

class Main(QMainWindow):
  def __init__(self):
    super(Main, self).__init__()

    self.layout = MainWidget()
    self.layout.MainSig.connect(self.__addTable)

    self.TableWid = ShowDBWidget()
    
    self.setCentralWidget(self.layout)
    self.__initUI()

  def __addTable(self, path):
    self.TableWid = ShowDBWidget(path)
    self.TableDock = QDockWidget("Tables", self)
    self.TableDock.setWidget(self.TableWid)
    self.TableDock.setMinimumSize(500, 500)
    self.TableDock.setAllowedAreas(Qt.AllDockWidgetAreas)
    self.addDockWidget(Qt.RightDockWidgetArea, self.TableDock, Qt.Horizontal)
    self.TableWid.TableSig.connect(self.__addSub)

  def __addSub(self, path, name):
    self.SubTableWid = ShowDBSubWidget(path, name)
    self.SubTableDock = QDockWidget("Elements", self)
    self.SubTableDock.setWidget(self.SubTableWid)
    self.SubTableDock.setMinimumSize(1000, 500)
    self.SubTableDock.setAllowedAreas(Qt.AllDockWidgetAreas)
    self.addDockWidget(Qt.RightDockWidgetArea, self.SubTableDock, Qt.Horizontal)

  def __initUI(self):
    menubar = self.menuBar()

    deleteAct = QAction('Delete', self)
    deleteAct.setShortcut('Delete')
    deleteAct.triggered.connect(self.layout.clickedDelete)

    clearAct = QAction('Clear', self)
    clearAct.setShortcut('Ctrl+W')
    clearAct.triggered.connect(self.layout.clickedClear)

    addAct = QAction('Add', self)
    addAct.setShortcut('Ctrl+O')
    addAct.triggered.connect(self.layout.clickedAdd)

    exitAct = QAction('Exit', self)
    exitAct.setShortcut('Esc')
    exitAct.triggered.connect(self.layout.clickedExit)

    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(addAct)
    fileMenu.addAction(deleteAct)
    fileMenu.addAction(clearAct)
    fileMenu.addAction(exitAct)

    self.setGeometry(1000, 500, 2000, 800)

class MainWidget(QWidget):
  MainSig = pyqtSignal(str)
  def __init__(self):
    super(MainWidget, self).__init__()
    
    self.__getDir()

    self.__DBList = QListWidget()
    self.__DBPathList = []
    self.__setDB()

    self.__delete = False

    self.setAcceptDrops(True)

    self.__initUI()
    
  def __initUI(self):
    self.__DBList.itemSelectionChanged.connect(self.__selectItem)
    self.__DBList.itemDoubleClicked.connect(self.__isDoubleClicked)
    
    addButton = QPushButton('Add')
    addButton.clicked.connect(self.clickedAdd)

    deleteButton = QPushButton('Delete')
    deleteButton.clicked.connect(self.clickedDelete)

    clearButton = QPushButton('Clear')
    clearButton.clicked.connect(self.clickedClear)

    exitButton = QPushButton('Exit')
    exitButton.clicked.connect(self.clickedExit)

    buttonLayout = QGridLayout()
    buttonLayout.addWidget(addButton, 0, 0)
    buttonLayout.addWidget(deleteButton, 0, 1)
    buttonLayout.addWidget(clearButton, 1, 0)
    buttonLayout.addWidget(exitButton, 1, 1)

    layout = QVBoxLayout()

    layout.addWidget(self.__DBList)
    layout.addLayout(buttonLayout)

    self.setLayout(layout)

  def __selectItem(self):
    if self.__delete:
      self.__delete = False
      return
    row = self.__DBList.row(self.__DBList.selectedItems()[0])
    self.__db_path = self.__DBPathList[row]

  def clickedExit(self):
    exit()

  def clickedClear(self):
    self.__DBList.clear()
    self.__DBPathList = []

  def clickedDelete(self):
    try:
      row = self.__DBList.row(self.__DBList.selectedItems()[0])
      self.__DBPathList.pop(row)
      self.__DBList.takeItem(row)
      self.__delete = True
    except:
      pass

  def clickedAdd(self):
    filename, ok = QFileDialog.getOpenFileNames(self, "Open File", self.__db_dir, filter = "db file(*.db)")
    if not ok:
      return
    for f in filename:
      f = f.replace('/', os.sep)
      if f in self.__DBPathList:
        return
      self.__DBList.addItem(os.path.basename(f))
      self.__DBPathList.append(f)

  def __isDoubleClicked(self):
    self.DB = ShowDBWidget(self.__db_path)
    self.MainSig.emit(self.__db_path)

  def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()
  
  def dropEvent(self, event):
    urls = event.mimeData().urls()
    for url in urls:
      path = url.toLocalFile().replace('/', os.sep)
      tmp = path.split(".")
      if path in self.__DBPathList:
        QMessageBox.information(self, "Warning", "This file already in.", QMessageBox.Ok)
        return
      if len(tmp) != 1:
        if self.__inExtension(tmp):
          self.__DBList.addItem(os.path.basename(path))
          self.__DBPathList.append(path)
      else:
        for roots, dirs, files in os.walk(tmp[0]):
          for f in files:
            if self.__inExtension(f):
              self.__DBList.addItem(os.path.basename(f))
              self.__DBPathList.append((roots + f).replace('/', os.sep))
  
          if len(dirs) != 0:
            self.__que = deque()
            for d in dirs:
              self.__que.append(d)
            self.__addDir()

  def __setDB(self):
    for roots, dirs, files in os.walk(self.__db_dir):
      for f in files:
        if self.__inExtension(f):
          self.__DBList.addItem(f)
          self.__DBPathList.append((roots + f).replace('/', os.sep))
      
      if len(dirs) != 0:
        self.__que = deque()
        for d in dirs:
          self.__que.append(d)
        self.__add_Dir()

  def __addDir(self):
    for roots, dirs, files in os.walk(self.__que.popleft()):
      for f in files:
        if self.__inExtension(f):
          self.__DBList.addItem(os.path.basename(f))
          self.__DBPathList.append((roots + f).replace('/', os.sep))
  
      if len(dirs) != 0:
        for d in dirs:
          self.__que.append(d)
        return self.__addDir()
  
    if len(self.__que) != 0:
      return self.__addDir()

  def __inExtension(self, item):
    try:
      if item.split(".")[-1] == "db":
        return True
    except:
      pass
    return False

  def __checkDir(self, dirname):
    if not os.path.exists(dirname):
      os.mkdir(dirname)
  
  def __getDir(self):
    self.__this_file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(self.__this_file_dir + '/../')
    self.__root_dir = (os.getcwd()).replace('/', os.sep)
  
    self.__db_dir = (self.__root_dir + '/DB/').replace('/', os.sep)
    self.__checkDir(self.__db_dir)

class ShowDBWidget(QWidget):
  TableSig = pyqtSignal(str, str)
  def __init__(self, db_path = None):
    super(ShowDBWidget, self).__init__()
    
    self.__db_path = db_path

    self.__tableList = QListWidget()
    self.__getTable()

    self.__initUI()
    
  def __initUI(self):
    self.__tableList.itemSelectionChanged.connect(self.__selectItem)
    self.__tableList.itemDoubleClicked.connect(self.__isDoubleClicked)

    layout = QVBoxLayout()
    layout.addWidget(self.__tableList)

    self.setLayout(layout)

  def __selectItem(self):
    self.__db_name = self.__tableList.selectedItems()[0].text()

  def __isDoubleClicked(self):
    self.sub = ShowDBSubWidget(self.__db_path, self.__db_name)
    self.TableSig.emit(self.__db_path, self.__db_name)
    
  def __getTable(self):
    if self.__db_path is None:
      return
    self.__conn = sqlite3.connect(self.__db_path)
    cur = self.__conn.cursor()
    cur.execute("select * from sqlite_master where type = 'table'")
    self.__tables = []
    while True:
      v = cur.fetchone()
      if v is None:
        break
      self.__tables.append(v[1])
    self.__tableList.addItems(self.__tables)
    cur.close()

class ShowDBSubWidget(QWidget):
  def __init__(self, path = None, db_name = None):
    super(ShowDBSubWidget, self).__init__()
    
    self.__db_path = path
    self.__db_name = db_name    
    self.__query = "select * from {} limit 1;".format(self.__db_name)
    self.__header = None

    self.__initUI()

  def __initUI(self):
    self.queryEdit = QTextEdit(self.__query)

    execButton = QPushButton("Execute")
    execButton.clicked.connect(self.__execQuery)

    editLayout = QHBoxLayout()
    editLayout.addWidget(self.queryEdit)
    editLayout.addWidget(execButton)

    self.__tree = MyTree(self.__db_path, self.__header, self.__query)

    layout = QVBoxLayout()
    layout.addWidget(self.__tree)
    layout.addLayout(editLayout)

    self.setLayout(layout)

  def __execQuery(self):
    self.__query = self.queryEdit.toPlainText().replace("\n", "")

    self.__tree._MyTree__setup(self.__db_path, self.__header, self.__query)

    self.__modelSetUp()
    self.__tree.setModel(self.__model)
  
  def __modelSetUp(self):
    self.__getHeader()
    self.__model = QStandardItemModel(0, len(self.__header))
    self.__setHeader()

  def __getHeader(self):
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()

    cur.execute(self.__query)
    self.__header = []

    for d in cur.description:
      self.__header.append(d[0])
    
    cur.close()
    conn.close()

  def __setHeader(self):
    for index, h in enumerate(self.__header):
      self.__model.setHeaderData(index, Qt.Horizontal, h)

class MyTree(QTreeView):
  def __init__(self, path, header, query):
    super(MyTree, self).__init__()
    
    self.setSortingEnabled(True)

  def __setup(self, path, header, query):
    self.__DBLister = DBLister(path, header, query)
    self.__DBLister.addIntObject.connect(self.__addItem)
    self.__DBLister.addStrObject.connect(self.__addItem)
    self.__DBLister.addDoubleObject.connect(self.__addItem)
    self.__DBLister.addBoolObject.connect(self.__addItem)
    self.__DBLister.setup()
    self.__DBLister.start()

  def __addItem(self, cnt, index, val):
    item = QStandardItem(str(val))
    model = self.model()
    model.setItem(cnt, index, item)

class DBLister(QThread):
  addIntObject = pyqtSignal(int, int, int)
  addStrObject = pyqtSignal(int, int, str)
  addDoubleObject = pyqtSignal(int, int, float)
  addBoolObject = pyqtSignal(int, int, bool)

  def __init__(self, path, header, query):
    super(DBLister, self).__init__()

    self.__db_path = path
    self.__header = header
    self.__query = query

    self.mutex = QMutex()

  def setup(self):
    self.stoped = False
  
  def stop(self):
    with QMutexLocker(self.mutex):
      self.stoped = True
  
  def run(self):
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()
    cur.execute(self.__query)
    cnt = 0
    while True:
      values = cur.fetchone()
      if values is None:
        break
      for index, v in enumerate(values):
        t = type(v)
        if t == int:
          self.addIntObject.emit(cnt, index, v)
        elif t == str:
          self.addStrObject.emit(cnt, index, v)
        elif t == float:
          self.addDoubleObject.emit(cnt, index, v)
        elif t == bool:
          self.addBoolObject.emit(cnt, index, v)
      cnt += 1

    cur.close()
    conn.close()
    self.stop()
    self.finished.emit()

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.finished.emit()
  
def main():
  app = QApplication(sys.argv)
  font = QFont("Meiryo")
  app.setFont(font)
  w = Main()
  w.setWindowTitle("SQLiteViewer")
  w.show()
  w.raise_()
  app.exec_()

if __name__ == '__main__':
  main()

import os
import sys

import numpy as np
import sqlite3
from collections import deque

from PyQt5.QtWidgets import (
  QApplication, 
  QListWidget, QWidget, QMainWindow, QDockWidget,
  QLineEdit, QPushButton,
  QTreeView,
  QAction, QSizePolicy,
  QMessageBox, QFileDialog, QProgressDialog,
  QGridLayout, QVBoxLayout, QHBoxLayout,
)

from PyQt5.QtCore import (
  Qt
)
from PyQt5.QtGui import (
  QFont, QStandardItemModel, QStandardItem
)

class Main(QMainWindow):
  def __init__(self):
    super(Main, self).__init__()

    self.layout = MainWidget()
    
    self.setCentralWidget(self.layout)
    self.__initUI()

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

    #sortAct = QAction('Sort', self)
    #sortAct.setShortcut('Ctrl+S')
    #sortAct.triggered.connect(self.layout.clickedSort)

    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(addAct)
    #fileMenu.addAction(sortAct)
    fileMenu.addAction(deleteAct)
    fileMenu.addAction(clearAct)
    fileMenu.addAction(exitAct)

    self.setGeometry(1000, 500, 800, 800)

class MainWidget(QWidget):
  def __init__(self):
    super(MainWidget, self).__init__()
    
    self.__getDir()

    self.__DBList = QListWidget()
    self.__DBPathList = []
    self.__setDB()

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
    except:
      pass

  def clickedAdd(self):
    filename, ok = QFileDialog.getOpenFileNames(self, "Open File", self.__db_dir, filter = "db file(*.db)")
    if not ok:
      return
    for f in filename:
      self.__DBList.addItem(os.path.basename(f))
      self.__DBPathList.append((f).replace('/', os.sep))

  def __isDoubleClicked(self):
    self.sub = ShowDBWidget(self.__db_path)
    self.sub.show()

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
  def __init__(self, db_path):
    super(ShowDBWidget, self).__init__()
    
    self.__db_path = db_path

    self.__tableList = QListWidget()
    self.__getTable()
    self.__initUI()
    
  def __initUI(self):
    self.__tableList.addItems(self.__tables)

    self.__tableList.itemSelectionChanged.connect(self.__selectItem)
    self.__tableList.doubleClicked.connect(self.__isDoubleClicked)

    """tree = QTreeView(self)
    self.model = QStandardItemModel(0, 1)
    self.model.setHeaderData(0, Qt.Vertical, 'table')
    self.model.appendRow(self.__tables)
    tree.setModel(self.model)
    tree.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)"""

    layout = QVBoxLayout()
    layout.addWidget(self.__tableList)

    self.setLayout(layout)

    self.resize(500, 800)

  def __selectItem(self):
    self.__db_name = self.__tableList.selectedItems()[0].text()

  def __isDoubleClicked(self):
    self.sub = ShowDBSubWidget(self.__db_path, self.__db_name)
    self.sub.show()

  def __getTable(self):
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()
    cur.execute("select * from sqlite_master where type = 'table'")
    self.__tables = []
    while True:
      v = cur.fetchone()
      if v is None:
        break
      #self.__tables.append(QStandardItem(v[1]))
      self.__tables.append(v[1])
    cur.close()
    conn.close()

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()

class ShowDBSubWidget(QWidget):
  def __init__(self, db_path, db_name):
    super(ShowDBSubWidget, self).__init__()
    
    self.__db_path = db_path
    self.__db_name = db_name

    self.__header = 0
    self.__getRow()
    self.__initUI()
    
  def __initUI(self):
    tree = QTreeView(self)
    tree.setSortingEnabled(True)
    self.model = QStandardItemModel(0, len(self.__header))
    self.__setHeader()
    tree.setModel(self.model)

    self.resize(500, 800)

  def __setHeader(self):
    for index, h in enumerate(self.__header):
      self.model.setHeaderData(index, Qt.Horizontal, h)

  def __getRow(self):
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()
    cur.execute("select * from {} limit 0".format(self.__db_name))
    self.__header = []
    for d in cur.description:
      self.__header.append(d[0])
    cur.close()
    conn.close()

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()

def main():
  app = QApplication(sys.argv)
  font = QFont("Meiryo")
  app.setFont(font)
  w = Main()
  w.setWindowTitle("title")
  w.show()
  w.raise_()
  app.exec_()

if __name__ == '__main__':
  main()

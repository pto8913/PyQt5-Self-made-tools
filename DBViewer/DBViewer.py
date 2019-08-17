import os
import sys

import sqlite3
from collections import deque

from PyQt5.QtWidgets import (
  QApplication, 
  QTreeView, QListWidget, 
  QMessageBox, QFileDialog,  
)

from PyQt5.QtCore import (
  Qt, QObject, QThread, pyqtSignal, QMutex, QMutexLocker, 
)
from PyQt5.QtGui import (
  QFont, QStandardItemModel, QStandardItem, 
)

from DBViewerUI import MainUI, DBListUI

basename = lambda x : os.path.basename(x)

class Notifier(QObject):
  notify = pyqtSignal()

class Thread(QThread):
  def __init__(self, notifier, name):
    super().__init__()
    
    self.notifier = notifier
    self.name = name
  
  def run(self):
    print('start thread :' + self.name)
    self.notifier.notify.emit()
    self.finished.emit()

class Main(MainUI):
  def __init__(self):
    super(Main, self).__init__()

    self.layout = MainWidget()
    self.setCentralWidget(self.layout)
    self.initUI()

class MainWidget(DBListUI):
  def __init__(self):
    super(MainWidget, self).__init__()
    
    self.__getDir()

    self.DBList = QListWidget()
    self.__DBPathList = []
    self.__addDir(self.__db_dir)

    self.DBList.itemSelectionChanged.connect(self.selectDBItem)
    self.DBList.itemDoubleClicked.connect(self.isDBItemDoubleClicked)

    self.tableList = QListWidget()
    self.tableList.itemSelectionChanged.connect(self.selectTableItem)

    self.tree = MyTree()
    
    self.query = "select count(*) from table ;"

    self.setAcceptDrops(True)

    self.initUI()

  def execQuery(self):
    #print(self.__db_path)
    self.query = self.queryEdit.toPlainText().replace("\n", " ")
    
    res = self.modelSetUp()
    if not res:
      return False

    check = self.__checkQuery()
    if check == 0:
      self.tree._MyTree__setup(self.__db_path, self.__header, self.query)
      if self.model:
        self.model.clear()
      self.modelSetUp()
      self.tree.setModel(self.model)
    elif check == 1:
      res = self.__InUpDelCreDrop()
      if res:
        QMessageBox.information(self, "Complete", "Finished change", QMessageBox.Ok)
    elif check == -1:
      QMessageBox.information(
        self, 
        "Warning", 
        """Please check your query and send a pull request or issue to my repository <br>
            <a href="https://github.com/pto8913/PyQt5-s-tools"> pto8913/PyQt5-s-tools </a><br>
        """, 
        QMessageBox.Ok)

  def __checkQuery(self):
    funcType = self.query.split(" ")[0].lower()

    if funcType == ("select"):
      return 0
    if funcType in ("insert", "update", "delete", "create", "drop", "alter"):
      return 1
    return -1

  def __InUpDelCreDrop(self):
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()

    try:
      cur.execute(self.__query)
    except sqlite3.Error as e:
      QMessageBox.information(self, "error", "{}".format(e), QMessageBox.Ok)
      cur.close()
      conn.close()
      return False
    conn.commit()
    cur.close()
    conn.close()
    return True

  def modelSetUp(self):
    if not self.query:
      return False
    res = self.__getHeader()
    if not res:
      return False
    self.model = QStandardItemModel(0, len(self.__header))
    self.__setHeader()
    return True

  def __getHeader(self):
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()

    try:
      cur.execute(self.query)
    except sqlite3.Error as e:
      QMessageBox.information(self, "error", "{}".format(e), QMessageBox.Ok)
      cur.close()
      conn.close()
      return False
    self.__header = []

    for d in cur.description:
      self.__header.append(d[0])
    
    cur.close()
    conn.close()
    return True

  def __setHeader(self):
    for index, h in enumerate(self.__header):
      self.model.setHeaderData(index, Qt.Horizontal, h)

  def selectTableItem(self):
    self.__db_name = self.tableList.selectedItems()[0].text()
    self.query = "select count(*) from {};".format(self.__db_name)
    self.queryEdit.setText(self.query)

  def __getTable(self):
    if self.__db_path is None:
      return
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()
    cur.execute("select * from sqlite_master where type = 'table'")
    self.__tables = []
    while True:
      v = cur.fetchone()
      if v is None:
        break
      self.__tables.append(v[1])
    self.tableList.addItems(self.__tables)
    cur.close()
    conn.close()
    
  def selectDBItem(self):
    try:
      row = self.DBList.row(self.DBList.selectedItems()[0])
      self.__db_path = self.__DBPathList[row]
    except:
      return

  def clickedExit(self):
    exit()

  def clickedClear(self):
    self.DBList.clear()
    self.__DBPathList = []

  def clickedDelete(self):
    try:
      row = self.DBList.row(self.DBList.selectedItems()[0])
      self.__DBPathList.pop(row)
      self.DBList.takeItem(row)
    except:
      pass

  def clickedAdd(self):
    filename, ok = QFileDialog.getOpenFileNames(self, "Open File", self.__db_dir, filter = "db file(*.db)")
    if not ok:
      return
    for f in filename:
      f = self.__adjustSep(f)
      if f in self.__DBPathList:
        continue
      self.DBList.addItem(basename(f))
      self.__DBPathList.append(f)

  def isDBItemDoubleClicked(self):
    self.__getTable()

  def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()
  
  def dropEvent(self, event):
    urls = event.mimeData().urls()
    for url in urls:
      path = self.__adjustSep(url.toLocalFile())
      tmp = path.split(".")
      if path in self.__DBPathList:
        QMessageBox.information(self, "Warning", "This file already in.", QMessageBox.Ok)
        return
      if len(tmp) != 1:
        if self.__inExtension(tmp):
          self.DBList.addItem(basename(path))
          self.__DBPathList.append(path)
      else:
        self.__addDir(tmp[0])

  def __addDir(self, item):
    for roots, dirs, files in os.walk(item):
      for f in files:
        if self.__inExtension(f):
          self.DBList.addItem(basename(f))
          self.__DBPathList.append(self.__adjustSep(roots + '/' + f))
  
      if len(dirs) != 0:
        for d in dirs:
          self.__que.append(d)
        return self.__addDir(self.__que.popleft())
    try:
      if len(self.__que) != 0:
        return self.__addDir(self.__que.popleft())
    except:
      return

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
    os.chdir(self.__this_file_dir)
    self.__root_dir = (os.getcwd()).replace('/', os.sep)
  
    self.__db_dir = (self.__root_dir + '/DB/').replace('/', os.sep)
    self.__checkDir(self.__db_dir)
    self.__addDirPath((self.__this_file_dir, self.__db_dir))

  def __addDirPath(self, paths):
    for path in paths:
      sys.path.append(path)

  def __adjustSep(self, path):
    return path.replace('/', os.sep)
  
class MyTree(QTreeView):
  def __init__(self, path = None, header = None, query = None):
    super(MyTree, self).__init__()
    
    if path is None or header is None or query is None:
      return

    self.setSortingEnabled(True)

  def __setup(self, path, header, query):
    self.__DBLister = DBLister(path, header, query)
    self.__DBLister.addIntObject.connect(self.__addItem)
    self.__DBLister.addStrObject.connect(self.__addItem)
    self.__DBLister.addDoubleObject.connect(self.__addItem)
    self.__DBLister.addBoolObject.connect(self.__addItem)
    
    self.__DBLister.setup()
    self.__DBLister.start()
    
  def __ext(self, e):
    self.exceptSig.emit(e)

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
    try:
      cur.execute(self.__query)
    except sqlite3.Error:
      self.finished.emit()
      return 
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
  w.setWindowTitle("SQLiteViewerTest")
  w.show()
  w.raise_()
  app.exec_()

if __name__ == '__main__':
  main()

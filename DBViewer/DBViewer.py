import os
import sys

import sqlite3

from PyQt5.QtWidgets import (
  QApplication, QListWidget, QMessageBox,   
)

from PyQt5.QtCore import (
  Qt, QObject, QThread, pyqtSignal
)

from PyQt5.QtGui import (
  QFont, QStandardItemModel, 
)

from DBViewerUI import MainUI, DBListUI
from DBViewerDirSetting import DirSetting as Ds
from DBViewerUIFunc import MyTree

basename = lambda x : os.path.basename(x)

def adjustSep(path):
  return path.replace('/', os.sep)

def inExtension(item, ext):
  try:
    if item.split(".")[-1] == ext:
      return True
  except:
    pass
  return False

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
    
    self.__db_dir = Ds().getDir()

    self.DBList = QListWidget()
    self.DBPathList = []
    self.DBList.itemSelectionChanged.connect(self.selectDBItem)
    self.DBList.itemDoubleClicked.connect(self.isDBItemDoubleClicked)

    self._DBListUI__addDir(self.__db_dir)

    self.tableList = QListWidget()
    self.tableList.itemSelectionChanged.connect(self.selectTableItem)

    self.tree = MyTree()
    
    self.query = "select count(*) from table;"
    self.pre_query = ""
    self.__isQueryChanged = False

    self.setAcceptDrops(True)

    self.initUI()

  # -------------------------------- Execute Query ----------------------------------
  
  def execQuery(self):
    #print(self.__db_path)
    self.query = self.queryEdit.toPlainText().replace("\n", " ")
    print(self.query)

    if self.query not in ("select count(*) from table;", "Create your table!"):
      self.__isQueryChanged = True

    check = self.checkQueryType(self.query)
    if check == 0:
      res = self.modelSetUp()
      if not res:
        return False

      self.pre_query = self.query
      self.tree._MyTree__setup(self.__db_path, self.__header, self.query)

      if self.model:
        self.model.clear()
      self.modelSetUp()
      self.tree.setModel(self.model)

    elif check == 1:
      QMessageBox.information(self, "Complete", "Finished change", QMessageBox.Ok)

    elif check == -1:
      QMessageBox.information(
        self, 
        "Warning", 
        """Please check your query and send a pull request or issue to my repository <br>
            <a href="https://github.com/pto8913/PyQt5-s-tools"> pto8913/PyQt5-s-tools </a><br>
        """, 
        QMessageBox.Ok)
  
  # -----------------------------------------------------------------------------------

  # ------------------------------- For Execute Query ---------------------------------

  def checkQueryType(self, item):
    funcType = item.split(" ")[0].lower()

    if funcType == ("select"):
      return 0

    if funcType in ("create", "drop"):
      if funcType == "create" and item.split(" ")[1].lower() == "database":
        self.CreateDB(item.split(" ")[-1].replace(";", ""))
        return 1
      self.CreatOrDropTable()
      return 1

    if funcType in ("insert", "update", "delete", "alter"):
      self.UpdateList()
      if not self.pre_query:
        return 1
      self.query = self.pre_query
      return 0
    return -1

  def CreatOrDropTable(self):
    try:
      conn = sqlite3.connect(self.__db_path)
      cur = conn.cursor()

      cur.execute(self.query)
      conn.commit()
      if self.tableList:
        self.tableList.clear()
      self.__getTable()
    except sqlite3.Error as e:
      QMessageBox.information(self, "error", "{}".format(e), QMessageBox.Ok)
    cur.close()
    conn.close()
    return True

  def CreateDB(self, name):
    try:
      if not inExtension(name, "db"):
        name += ".db"
    except:
      pass
    conn = sqlite3.connect(self.__db_dir + name)
    conn.close()
    self.DBList.addItem(name)
    self.DBPathList.append(self.__db_dir + name)
    self.query.setText("Create your table!")
    return True

  def UpdateList(self):
    conn = sqlite3.connect(self.__db_path)
    cur = conn.cursor()

    try:
      cur.execute(self.query)
    except sqlite3.Error as e:
      QMessageBox.information(self, "error", "{}".format(e), QMessageBox.Ok)
      cur.close()
      conn.close()
      return False
    conn.commit()
    cur.close()
    conn.close()
    return True

  # -----------------------------------------------------------------------------------

  # ------------------------------------ DB Func --------------------------------------

  def selectDBItem(self):
    try:
      row = self.DBList.row(self.DBList.selectedItems()[0])
      self.__db_path = self.DBPathList[row]
    except:
      return

  def isDBItemDoubleClicked(self):
    if len(self.tableList) != 0:
      self.tableList.clear()
    self.__getTable()

  # -----------------------------------------------------------------------------------

  # ----------------------------------- Set Table -------------------------------------

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
  
  def modelSetUp(self):
    if not self.query or not self.__isQueryChanged:
      return False

    res = self.__getHeader()
    if not res:
      return False

    self.model = QStandardItemModel(0, len(self.__header))
    self.__setHeader()
    return True

  def __setHeader(self):
    for index, h in enumerate(self.__header):
      self.model.setHeaderData(index, Qt.Horizontal, h)

  # -----------------------------------------------------------------------------------

  # ---------------------------------- Table Func -------------------------------------

  def selectTableItem(self):
    try:
      self.__db_name = self.tableList.selectedItems()[0].text()
      self.query = "select count(*) from {};".format(self.__db_name)
      self.__isQueryChanged = True
    except:
      self.query = "select count(*) from table;"
      self.__isQueryChanged = False
    self.queryEdit.setText(self.query)
    return True

  # -----------------------------------------------------------------------------------
    
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

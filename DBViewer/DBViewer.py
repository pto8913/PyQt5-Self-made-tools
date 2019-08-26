import sys

from sqlite3 import connect, Error

from PyQt5.QtWidgets import (
  QApplication, QListWidget, QMessageBox,   
)

from PyQt5.QtCore import (
  Qt, QObject, QThread, pyqtSignal
)

from PyQt5.QtGui import (
  QFont, QStandardItemModel, 
)

from DBViewer import (
  MainUI, DBListUI, DirSetting as Ds,
  MyTree, Notifier, Thread, 
  adjustSep, inExtension, basename,
)

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
    self.query = self.queryEdit.toPlainText().replace("\n", " ")

    if self.query not in ("select count(*) from table;"):
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
      QMessageBox.Critical(
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

      res = self.CreatOrDropTable()
      if res:
        return 1
      return -2

    if funcType in ("pragma", "insert", "update", "delete", "alter"):
      res = self.UpdateList()
      if not res:
        return -2
      if not self.pre_query:
        return 1

      self.query = self.pre_query
      return 0
    return -1

  def CreatOrDropTable(self):
    try:
      self.connectDB(self.__db_path)

      self.cur.execute(self.query)
      self.conn.commit()
      if self.tableList:
        self.tableList.clear()
      self.__getTable()

    except Error as e:
      QMessageBox.Critical(self, "error", "{}".format(e), QMessageBox.Ok)
      self.closeDB()
      return False

    self.closeDB()
    return True

  def CreateDB(self, name):
    try:
      if not inExtension(name, "db"):
        name += ".db"
    except:
      pass

    conn = connect(self.__db_dir + name)
    conn.close()
    self.DBList.addItem(name)
    self.DBPathList.append(self.__db_dir + name)
    return True

  def UpdateList(self):
    self.connectDB(self.__db_path)

    try:
      self.cur.execute(self.query)

    except Error as e:
      QMessageBox.Critical(self, "error", "{}".format(e), QMessageBox.Ok)
      self.closeDB()
      return False

    self.conn.commit()
    self.closeDB()
    return True

  # -----------------------------------------------------------------------------------

  # ------------------------------------ DB Func --------------------------------------

  def connectDB(self, name):
    self.conn = connect(name)
    self.cur = self.conn.cursor()

  def closeDB(self):
    self.cur.close()
    self.conn.close()

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
    self.connectDB(self.__db_path)
    self.cur.execute("select * from sqlite_master where type = 'table'")
    self.__tables = []
    while True:
      v = self.cur.fetchone()
      if v is None:
        break
      self.__tables.append(v[1])
    self.tableList.addItems(self.__tables)
    self.closeDB()

  def __getHeader(self):
    self.connectDB(self.__db_path)

    try:
      self.cur.execute(self.query)
    except Error as e:
      QMessageBox.Critical(self, "error", "{}".format(e), QMessageBox.Ok)
      self.closeDB()
      return False
    self.__header = []

    for d in self.cur.description:
      self.__header.append(d[0])
    
    self.closeDB()
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

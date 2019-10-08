import sys

from sqlite3 import connect, Error

from PyQt5.QtWidgets import (
  QApplication, QListWidget, QMessageBox,
  QTextEdit, 
)

from PyQt5.QtCore import (
  Qt, QObject, QThread, pyqtSignal
)

from PyQt5.QtGui import (
  QFont, QStandardItemModel, 
)

from DBViewer.DBViewerUI import MainUI, DBListUI
from DBViewer.DBViewerThread import MyTree, Notifier, Thread
from DBViewer.myfunc import function

basename = lambda x: function().basename(x)
inExtension = lambda x, ext: function().inExtension(x, ext)

from pathlib import Path

class Main(MainUI):
  def __init__(self):
    super(Main, self).__init__()

    self.layout = MainWidget()
    self.setCentralWidget(self.layout)
    self.initUI()

class MainWidget(DBListUI):
  def __init__(self):
    super(MainWidget, self).__init__()
    
    self.__DirInit()

    self.DBList = QListWidget()
    self.DBPathList = []
    self.DBList.itemSelectionChanged.connect(self.selectDBItem)
    self.DBList.itemDoubleClicked.connect(self.isDBItemDoubleClicked)

    self._DBListUI__addDir(self.db_dir)

    self.tableList = QListWidget()
    self.tableList.itemSelectionChanged.connect(self.selectTableItem)

    self.tree = MyTree()
    
    self.query = "select count(*) from table;"
    self.pre_query = ""
    self.__isQueryChanged = False

    self.setAcceptDrops(True)

    self.initUI()

    self.queryEdit.selectionChanged.connect(self.updateQuery)

  # -------------------------------- Execute Query ----------------------------------
  
  def execQuery(self):
    if self.query == "select count(*) from table;":
      self.query = self.queryEdit.toPlainText().replace("\n", " ").split(" ")
      queries = self.__deleteSpa(self.query)
      self.query = " ".join(queries)

    if self.query.count(';') > 1:
      queries = self.queryEdit.toPlainText().replace("\n", " ").split(";")
      queries = self.__deleteSpa(queries)
      # print(queries)
      self.query = queries[-1]

    if self.query != "select count(*) from table;":
      self.__isQueryChanged = True

    # print(self.query)

    check = self.checkQueryType(self.query)
    # 0 : select ~
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

    # 1 : create, drop, pragma, delete, update, alter
    elif check == 1:
      QMessageBox.information(self, "Complete", "Finished change", QMessageBox.Ok)

    elif check == -1:
      print(self.query)
      QMessageBox.critical(
        self, 
        "Warning", 
        """Please check your query and send a pull request or issue to my repository <br>
            <a href="https://github.com/pto8913/PyQt5-s-tools"> pto8913/PyQt5-s-tools </a><br>
        """, 
        QMessageBox.Ok)
  
  # -----------------------------------------------------------------------------------

  # ------------------------------- benri na function ---------------------------------
  def __deleteSpa(self, items):
    items = list(filter(lambda x: x != "" and x != " ", items))
    return items
  
  def keyPressEvent(self, event):
    if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Return:
      self.execQuery()

  # -----------------------------------------------------------------------------------

  # ----------------------------------- For Query -------------------------------------

  def updateQuery(self):
    cursor = self.queryEdit.textCursor()
    if not cursor.hasSelection():
      self.query = "select count(*) from table;"
      return
    self.query = cursor.selectedText().replace("\u2029", "")
    if self.query.count(';') > 1:
      queries = self.query.split(";")
      queries = self.__deleteSpa(queries)
      self.query = queries[-1]
      self.query = self.query

  # -----------------------------------------------------------------------------------

  # ------------------------------- For Execute Query ---------------------------------

  def checkQueryType(self, item):
    words = item.split(" ")
    words = self.__deleteSpa(words)
    # print(words)
    funcType = words[0].lower()

    if funcType == ("select"):
      return 0

    if funcType in ("create", "drop"):
      if funcType == "create" and words[1].lower() == "database":
        self.CreateDB(words[-1].replace(";", ""))
        return 1

      res = self.CreatOrDropTable(funcType)
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
      return 10
    return -1

  def CreatOrDropTable(self, func_type: str):
    try:
      self.connectDB(self.__db_path)

      self.cur.execute(self.query)
      if func_type == "drop":
        self.Vaccum()

      self.conn.commit()
      self.closeDB()
    except Error as e:
      QMessageBox.critical(self, "error", "{}".format(e), QMessageBox.Ok)
      self.closeDB()
      return False

    if self.tableList:
      self.tableList.clear()
    self.__getTable()

    return True

  def Vaccum(self):
    self.cur.execute("VACUUM")
   
  def CreateDB(self, name: str) -> None:
    try:
      if not inExtension(name, "db"):
        name += ".db"
    except:
      pass
    
    dbpath = self.db_dir.joinpath(name)
    conn = connect(str(dbpath))
    conn.close()
    self.DBList.addItem(name)
    self.DBPathList.append(dbpath)
    return True

  def UpdateList(self):
    self.connectDB(self.__db_path)

    try:
      self.cur.execute(self.query)

    except Error as e:
      QMessageBox.critical(self, "error", "{}".format(e), QMessageBox.Ok)
      self.closeDB()
      return False

    self.conn.commit()
    self.closeDB()
    if self.pre_query:
      self.query = self.pre_query
    return True

  # -----------------------------------------------------------------------------------

  # ------------------------------------ DB Func --------------------------------------

  def connectDB(self, name: str) -> None:
    self.conn = connect(str(name))
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
      QMessageBox.critical(self, "error", "{}".format(e), QMessageBox.Ok)
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

  # ----------------------------------- Init Func -------------------------------------

  def __DirInit(self) -> None:
    # current_dir = Path(__file__).parent.resolve()
    current_dir = Path().parent.resolve()

    self.db_dir = current_dir.joinpath("DB")
    self.__CheckDir(self.db_dir)

  def __CheckDir(self, item: str) -> None:
    if not item.exists():
      item.mkdir()

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
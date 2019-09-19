from PyQt5.QtWidgets import (
  QTreeView
)

from PyQt5.QtGui import (
  QStandardItem, QStandardItemModel
)

from PyQt5.QtCore import (
  Qt, QObject, QThread, pyqtSignal, QMutex, QMutexLocker, 
)

from sqlite3 import connect, Error

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
    conn = connect(self.__db_path)
    cur = conn.cursor()
    try:
      cur.execute(self.__query)
    except Error:
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
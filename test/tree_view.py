import sys
from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QTreeView, QMainWindow, QWidget
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

class ListTreeModel(QAbstractItemModel):
  def __init__(self, initdata):
    super().__init__()
    self.set_data(initdata)

  def set_data(self, init_data):
    self.__data = init_data

  def index(self, row, column, parent):
    if not parent.isValid():
      parentItem = self.__data
    else:
      parentItem = parent.internalPointer()

    if isinstance(parentItem, list):
      try:
        return self.createIndex(row, column, parentItem[row])
      except:
        pass
    return QModelIndex()

  def data(self, index, role = Qt.DisplayRole):
    item = index.internalPointer()
    if role == Qt.DisplayRole:
      if index.column() == 0:
        return str(item)
      else:
        return "display"
    elif role == Qt.UserRole:
      if index.column() == 0:
        return item
      else:
        return "user"
    else:
      return None

  def rowCount(self, index):
    if not index.isValid():
      owner = self.__data
    else:
      owner = index.internalPointer()
    if isinstance(owner, list):
      return len(owner)
    else:
      return 1
  
  def columnCount(self, parent):
    return 1

  def find_parent(self, item, searchlist = None):
    if searchlist is None:
      searchlist = self.__data
    if isinstance(searchlist, list):
      for i, s in enumerate(searchlist):
        if s is item:
          return i, s
        else:
          pos, rlist = self.find_parent(item, s)
          if rlist is not None:
            return pos, rlist
    return None, None
  
  def parent(self, index):
    item = index.internalPointer()
    r, parentitem = self.find_parent(item)
    if parentitem is None or parentitem == self.__data:
      return QModelIndex()
    else:
      return self.createIndex(r, 0, parentitem)
    
  def headerData(self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      if section == 0:
        return "test"
      else:
        return "detail"

class a(QWidget):
  def __init__(self):
    super().__init__()
    data = ['1',['2',['3','4'],'5','6'],'7',['8','9'],'10']
    tree = ListTreeModel(data)
    model = QTreeView(self)
    model.setModel(tree)
    

def main():
  app = QApplication(sys.argv)
  w = a()
  w.show()
  w.raise_()
  app.exec_()

if __name__ == '__main__':
  main()

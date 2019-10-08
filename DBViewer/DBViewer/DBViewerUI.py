from PyQt5.QtWidgets import (
  QMainWindow, QWidget, 
  QAction, QPushButton, QMessageBox, 
  QGridLayout, QVBoxLayout, QHBoxLayout,
  QLineEdit, QTextEdit, QFileDialog, 
)

from collections import deque

from pathlib import Path

from DBViewer.myfunc import function

basename = lambda x: function().basename(x)
inExtension = lambda x, ext: function().inExtension(x, ext)

class MainUI(QMainWindow):
  def initUI(self):
    menubar = self.menuBar()

    deleteAct = QAction('Delete', self)
    deleteAct.setShortcut('Delete')

    clearAct = QAction('Clear', self)
    clearAct.setShortcut('Ctrl+W')

    addAct = QAction('Add', self)
    addAct.setShortcut('Ctrl+O')

    exitAct = QAction('Exit', self)
    exitAct.setShortcut('Esc')

    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(addAct)
    fileMenu.addAction(deleteAct)
    fileMenu.addAction(clearAct)
    fileMenu.addAction(exitAct)

    self.setGeometry(500, 500, 1500, 800)

    deleteAct.triggered.connect(self.layout.clickedDelete)
    clearAct.triggered.connect(self.layout.clickedClear)
    addAct.triggered.connect(self.layout.clickedAdd)
    exitAct.triggered.connect(self.layout.clickedExit)

class DBListUI(QWidget):
  def initUI(self):
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

    inputLayout = QVBoxLayout()

    self.DBList.setMinimumSize(300, 500)
    inputLayout.addWidget(self.DBList)
    inputLayout.addLayout(buttonLayout)

    self.queryEdit = QTextEdit(self.query)

    execButton = QPushButton("Execute")
    execButton.clicked.connect(self.execQuery)
      
    editLayout = QHBoxLayout()
    editLayout.addWidget(self.queryEdit)
    editLayout.addWidget(execButton)

    tableLayout = QVBoxLayout()
    self.tree.setMinimumSize(1200, 500)
    tableLayout.addWidget(self.tree)
    tableLayout.addLayout(editLayout)

    layout = QHBoxLayout()
    self.tableList.setMinimumSize(300, 500)
    layout.addLayout(inputLayout)
    layout.addWidget(self.tableList)
    layout.addLayout(tableLayout)

    self.setLayout(layout)

  # ----------------------------------- UI Func --------------------------------------

  def clickedExit(self):
    exit()

  def clickedClear(self):
    self.DBList.clear()
    self.DBPathList = []

  def clickedDelete(self):
    ret = QMessageBox.information(self, "Delete", "If Delete from List, Yes. <br> Delete from PC, No.", QMessageBox.Yes | QMessageBox.Cancel)
    if ret == QMessageBox.Yes:
      try:
        row = self.DBList.row(self.DBList.selectedItems()[0])
        self.DBPathList.pop(row)
        self.DBList.takeItem(row)
      except:
        return None
    elif ret == QMessageBox.Cancel:
      return None

  def clickedAdd(self):
    filename, ok = QFileDialog.getOpenFileNames(self, "Open File", str(self.db_dir), filter = "db file(*.db)")
    if not ok:
      return None
    for f in filename:
      f = Path(f)
      if f in self.DBPathList:
        continue
      self.DBList.addItem(basename(f))
      self.DBPathList.append(f)
  
  # -----------------------------------------------------------------------------------

  # ------------------------------ Set DBList (DnD) -----------------------------------

  def dragEnterEvent(self, event) -> None:
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()

  def dropEvent(self, event) -> None:
    urls = event.mimeData().urls()
    for url in urls:
      path = url.toLocalFile()
      x = Path(path)
      tmp = path.split('.')
      if x in self.DBPathList:
        QMessageBox.information(self, 'Warning', 'This file already in.', QMessageBox.Ok)
        continue
      if len(tmp) != 1:
        if inExtension(x, "db"):
          self.DBList.addItem(x.name)
          self.DBPathList.append(x)
      else:
        print(tmp[0])
        self.__addDir(Path(tmp[0]))
  
  def __addDir(self, item: str) -> None:
    for f in list(item.glob("**/*.db")):
      self.DBList.addItem(f.name)
      self.DBPathList.append(f)

  # -----------------------------------------------------------------------------------
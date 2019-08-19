from PyQt5.QtWidgets import (
  QWidget, QMainWindow,
  QAction, QMessageBox, QPushButton,
  QGridLayout, QVBoxLayout, 
)

class MainUI(QMainWindow):
  def initUI(self):
    self.statusBar().showMessage('')

    menubar = self.menuBar()

    startAct = QAction('Start', self)
    startAct.setShortcut('Enter')
    startAct.triggered.connect(self.main_process.onClicked)

    deleteAct = QAction('Delete', self)
    deleteAct.setShortcut('Delete')
    deleteAct.triggered.connect(self.main_process.clickedDelete)

    clearAct = QAction('Clear', self)
    clearAct.setShortcut('Ctrl+W')
    clearAct.triggered.connect(self.main_process.clickedClear)

    addAct = QAction('Add', self)
    addAct.setShortcut('Ctrl+O')
    addAct.triggered.connect(self.main_process.clickedAdd)

    exitAct = QAction('Exit', self)
    exitAct.setShortcut('Esc')
    exitAct.triggered.connect(self.main_process.clickedExit)

    sortAct = QAction('Sort', self)
    sortAct.setShortcut('Ctrl+S')
    sortAct.triggered.connect(self.main_process.clickedSort)

    helpAct = QAction('Help', self)
    helpAct.setShortcut('Ctrl+H')
    helpAct.triggered.connect(self.__clickedHelp)

    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(addAct)
    fileMenu.addAction(sortAct)
    fileMenu.addAction(startAct)
    fileMenu.addAction(deleteAct)
    fileMenu.addAction(clearAct)
    fileMenu.addAction(exitAct)
    fileMenu.addAction(helpAct)

    self.setGeometry(1000, 500, 800, 800)

  def __clickedHelp(self):
    QMessageBox.information(
      self, 
      "Help", 
      " <center> This is xml_to_sqlite app </center> \
        <h4> First: </h4> \
          You should to get 5m DEM(Digital Elevation Data) from here: \
          <a href = \"https://www.gsi.go.jp/kiban/index.html\"> 国土地理院 </a> \
        <h4> Second: </h4> \
          insert DEMdata to db from this app \
        <h4> Finally </h4> \
          You can enjoy landscape on main.py",
      QMessageBox.Ok
    )

class MainProcessUI(QWidget):
  def initUI(self):
    startButton = QPushButton("Start")
    startButton.clicked.connect(self.onClicked)

    exitButton = QPushButton("Exit")
    exitButton.clicked.connect(self.clickedExit)

    sortButton = QPushButton("Sort Item")
    sortButton.clicked.connect(self.clickedSort)

    addButton = QPushButton("Add Item")
    addButton.clicked.connect(self.clickedAdd)

    deleteButton = QPushButton("Delete Item")
    deleteButton.clicked.connect(self.clickedDelete)

    clearButton = QPushButton("Clear Item")
    clearButton.clicked.connect(self.clickedClear)

    buttonLayout = QGridLayout()
    buttonLayout.addWidget(startButton, 0, 0)
    buttonLayout.addWidget(addButton, 0, 1)
    buttonLayout.addWidget(sortButton, 0, 2)
    buttonLayout.addWidget(deleteButton, 1, 0)
    buttonLayout.addWidget(clearButton, 1, 1)
    buttonLayout.addWidget(exitButton, 1, 2)

    layout = QVBoxLayout()
    layout.addWidget(self.FileList)
    layout.addLayout(buttonLayout)

    self.setLayout(layout)
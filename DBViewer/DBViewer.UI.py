from PyQt5.QtWidgets import (
  QMainWindow, QWidget, 
  QAction, QPushButton,
  QGridLayout, QVBoxLayout, QHBoxLayout,
  QLineEdit, QTextEdit, 
)

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

    self.setGeometry(100, 100, 1500, 800)

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
    self.tree.setMinimumSize(1000, 500)
    tableLayout.addWidget(self.tree)
    tableLayout.addLayout(editLayout)

    layout = QHBoxLayout()
    self.tableList.setMinimumSize(300, 500)
    layout.addLayout(inputLayout)
    layout.addWidget(self.tableList)
    layout.addLayout(tableLayout)

    self.setLayout(layout)

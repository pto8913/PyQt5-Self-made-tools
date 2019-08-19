from PyQt5.QtWidgets import (
  QMainWindow, QAction,
)

class MainUI(QMainWindow):
  def initUI(self):
    menubar = self.menuBar()

    openAct = QAction('&Open', self)
    openAct.setShortcut('Ctrl+O')
    openAct.triggered.connect(self.openFile)

    exitAct = QAction('&Exit', self)
    exitAct.setShortcut('Ctrl+Q')
    exitAct.triggered.connect(self.close)

    saveAct = QAction('&Save', self)
    saveAct.setShortcut('Ctrl+S')
    saveAct.triggered.connect(self.saveFile)

    resetAct = QAction('&Reset', self)
    resetAct.triggered.connect(self.canvas.resetImage)

    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(resetAct)
    fileMenu.addAction(openAct)
    fileMenu.addAction(saveAct)
    fileMenu.addAction(exitAct)

    selectColorAct = QAction('&Pen Color', self)
    selectColorAct.triggered.connect(self.selectColor)

    selectWidthAct = QAction('&Pen Width', self)
    selectWidthAct.triggered.connect(self.selectWidth)

    backAct = QAction('&Back', self)
    backAct.setShortcut('Ctrl+Z')
    backAct.triggered.connect(self.canvas.backImage)

    nextAct = QAction('&Next', self)
    nextAct.setShortcut('Ctrl+Y')
    nextAct.triggered.connect(self.canvas.nextImage)

    penColorMenu = menubar.addMenu('&Pen Color')
    penColorMenu.addAction(selectColorAct)
    penWidthMenu = menubar.addMenu('&Pen Width')
    penWidthMenu.addAction(selectWidthAct)
    backMenu = menubar.addMenu('&Back')
    backMenu.addAction(backAct)
    nextMenu = menubar.addMenu('&Next')
    nextMenu.addAction(nextAct)

    self.setGeometry(300, 300, 1000, 500)
    self.setWindowTitle("MainWindow")
    self.show()
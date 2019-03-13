import sys
from PyQt5.QtWidgets import (
  QWidget, QPushButton, QApplication, QLineEdit, QGridLayout, QVBoxLayout
)
class App(QWidget):
  def __init__(self):
    super().__init__()
    self.initUI()
  
  def initUI(self):
    self.lineEdit = QLineEdit(self)
    vbox = QVBoxLayout()
    vbox.addWidget(self.lineEdit)

    grid = QGridLayout()
    buttonC = QPushButton("C", self)
    grid.addWidget(buttonC, 1, 1)
    buttonBack = QPushButton("Back", self)
    grid.addWidget(buttonBack, 1, 2)
    buttonClose = QPushButton("Close", self)
    grid.addWidget(buttonClose, 1, 4)
    button7 = QPushButton("7", self)
    grid.addWidget(button7, 2, 1)
    button8 = QPushButton("8", self)
    grid.addWidget(button8, 2, 2)
    button9 = QPushButton("9", self)
    grid.addWidget(button9, 2, 3)
    buttonDiv = QPushButton("/", self)
    grid.addWidget(buttonDiv, 2, 4)
    button4 = QPushButton("4", self)
    grid.addWidget(button4, 3, 1)
    button5 = QPushButton("5", self)
    grid.addWidget(button5, 3, 2)
    button6 = QPushButton("6", self)
    grid.addWidget(button6, 3, 3)
    buttonMul = QPushButton("*", self)
    grid.addWidget(buttonMul, 3, 4)
    button1 = QPushButton("1", self)
    grid.addWidget(button1, 4, 1)
    button2 = QPushButton("2", self)
    grid.addWidget(button2, 4, 2)
    button3 = QPushButton("3", self)
    grid.addWidget(button3, 4, 3)
    buttonMin = QPushButton("-", self)
    grid.addWidget(buttonMin, 4, 4)
    button0 = QPushButton("0", self)
    grid.addWidget(button0, 5, 1)
    buttonCom = QPushButton(".", self)
    grid.addWidget(buttonCom, 5, 2)
    buttonEq = QPushButton("=", self)
    grid.addWidget(buttonEq, 5, 3)
    buttonPls = QPushButton("+", self)
    grid.addWidget(buttonPls, 5, 4)

    vbox.addLayout(grid)
    self.setLayout(vbox)

    button0.clicked.connect(self.clickedButton)
    button1.clicked.connect(self.clickedButton)
    button2.clicked.connect(self.clickedButton)
    button3.clicked.connect(self.clickedButton)
    button4.clicked.connect(self.clickedButton)
    button5.clicked.connect(self.clickedButton)
    button6.clicked.connect(self.clickedButton)
    button7.clicked.connect(self.clickedButton)
    button8.clicked.connect(self.clickedButton)
    button9.clicked.connect(self.clickedButton)
    buttonMul.clicked.connect(self.clickedButton)
    buttonPls.clicked.connect(self.clickedButton)
    buttonDiv.clicked.connect(self.clickedButton)
    buttonMin.clicked.connect(self.clickedButton)
    buttonCom.clicked.connect(self.clickedButton)
    buttonClose.clicked.connect(self.clickedCloseButton)
    buttonEq.clicked.connect(self.clickedEqualButton)
    buttonC.clicked.connect(self.clickedCButton)
    buttonBack.clicked.connect(self.clickedBackButton)

    self.setGeometry(300, 300, 200, 200)
    self.setWindowTitle('Calculator')
    self.show()

  def clickedEqualButton(self):
    try:
      inp = eval(self.lineEdit.text())
    except:
      inp = ""
    self.lineEdit.setText(str(inp))

  def clickedCButton(self):
    self.lineEdit.setText("0")

  def clickedBackButton(self):
    self.lineEdit.setText(self.lineEdit.text()[:-1])

  def clickedButton(self):
    sender = self.sender()
    self.lineEdit.setText(self.lineEdit.text()+sender.text())

  def clickedCloseButton(self):
    self.close()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = App()
  sys.exit(app.exec_())
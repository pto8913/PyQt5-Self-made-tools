import sys
from PyQt5.QtWidgets import (
  QApplication, QLineEdit
)

from PyQt5.QtGui import QFont

from calculatorUI import MainUI

class Main(MainUI):
    def __init__(self):
        super().__init__()
        self.initUI()
    
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

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = Main()
    w.setWindowTitle('calculator')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()
from PyQt5.QtWidgets import (
    QMainWindow, QGridLayout, QPushButton, 
)

class SaveVideoUI(QMainWindow):
    def InitUI(self):
        StartButton = QPushButton("Start")

        ExitButton = QPushButton("Exit")

        ButtonLayout = QGridLayout()
        ButtonLayout.addWidget(StartButton, 0, 0)
        ButtonLayout.addWidget(ExitButton, 0, 1)

        self.setGeometry(0, 0, 1000, 400)
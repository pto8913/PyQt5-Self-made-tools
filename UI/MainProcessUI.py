from PyQt5.QtWidgets import (
    QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLineEdit, QWidget
)
import sys

class MainProcessUI(QWidget):
    def InitUI(self):
        StartButton = QPushButton("Start")
        StartButton.clicked.connect(self.OnClickedStart)

        AddFileButton = QPushButton("Add File")
        AddFileButton.clicked.connect(self.OnClickedAddFile)

        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(self.OnClickedExit)

        ButtonLayout = QGridLayout()
        ButtonLayout.addWidget(StartButton, 0, 0)
        ButtonLayout.addWidget(AddFileButton, 0, 1)
        ButtonLayout.addWidget(ExitButton, 1, 1)

        self.FileWidget = QListWidget()
        self.FailedItemList = QListWidget()

        

        self.DBNameLine = QLineEdit("DBName")
        self.TableNameLine = QLineEdit("TableName")

        self.Layout = QVBoxLayout()
        self.Layout.addWidget(self.FileWidget)
        self.Layout.addWidget(self.DBNameLine)
        self.Layout.addWidget(self.TableNameLine)
        self.Layout.addLayout(ButtonLayout)

        entire = QHBoxLayout()

        entire.addLayout(self.Layout)
        entire.addWidget(self.FailedItemList)

        self.setLayout(entire)

    def OnClickedExit(self):
        self.ForceQuitMusicTearOffThread()
        sys.exit()
    
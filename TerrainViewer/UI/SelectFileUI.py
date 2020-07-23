# --- STL ---
import sys
from pathlib import Path
from typing import Dict

# --- PL ---
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, 
    QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal

# --- MyL ---


class SelectFileUI(QWidget):
    BEGIN_CreateTerrainDelegate = pyqtSignal(dict)

    def __init__(self, NumOfFile: int) -> None:
        super(SelectFileUI, self).__init__()
        
        self.NumOfFile = NumOfFile
        self.FileListForDisplay = [[] for i in range(NumOfFile // 10)]
        self.SelectedFiles = {}
        self.InitUI()

    def InitUI(self) -> None:
        self.SelectFileList = QGridLayout()

        for i in range(self.NumOfFile):
            button = QPushButton(str(i))
            button.setCheckable(True)
            self.SelectFileList.addWidget(button, i // 10, i % 10)
            button.toggled.connect(self.OnFileToggled)
        
        DefiniteButton = QPushButton("Definite")
        DefiniteButton.clicked.connect(self.OnClickedDefinite)
        CancelButton = QPushButton("Cancel")
        CancelButton.clicked.connect(self.OnClickedCancel)

        ButtonLayout = QHBoxLayout()
        ButtonLayout.addWidget(DefiniteButton)
        ButtonLayout.addWidget(CancelButton)

        Layout = QVBoxLayout()
        Layout.addLayout(self.SelectFileList)
        Layout.addLayout(ButtonLayout)

        self.setLayout(Layout)

    def OnFileToggled(self, checked: bool) -> None:
        if checked:
            self.SelectedFiles[self.sender().text()] = True
        else:
            self.SelectedFiles.pop(self.sender().text())

    def OnClickedDefinite(self) -> pyqtSignal(Dict[str, bool]):
        for k in self.SelectedFiles.keys():
            print(k)
        self.BEGIN_CreateTerrainDelegate.emit(self.SelectedFiles)

    def OnClickedCancel(self) -> None:
        self.close()
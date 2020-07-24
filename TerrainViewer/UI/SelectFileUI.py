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
    CANCEL_SelectFileDelegate = pyqtSignal()

    def __init__(self, NumOfFile: int) -> None:
        super(SelectFileUI, self).__init__()
        
        self.NumOfFile = NumOfFile
        self.FileListForDisplay = [[] for i in range(NumOfFile // 10)]
        self.SelectedFiles = {}
        self.InitUI()

    def InitUI(self) -> None:
        self.SelectFileLayout = QGridLayout()

        for i in range(self.NumOfFile):
            button = QPushButton(str(i))
            button.setCheckable(True)
            self.SelectFileLayout.addWidget(button, i // 10, i % 10)
            button.toggled.connect(self.OnFileToggled)
        
        SelectAllButton = QPushButton("Select All")
        SelectAllButton.clicked.connect(self.OnClickedSelectAll)

        DeselectAllButton = QPushButton("Deselect All")
        DeselectAllButton.clicked.connect(self.OnClickedDeselectAll)

        DefiniteButton = QPushButton("Definite")
        DefiniteButton.clicked.connect(self.OnClickedDefinite)

        CancelButton = QPushButton("Cancel")
        CancelButton.clicked.connect(self.OnClickedCancel)

        ButtonLayout = QGridLayout()
        ButtonLayout.addWidget(SelectAllButton, 0, 0)
        ButtonLayout.addWidget(DeselectAllButton, 0, 1)
        ButtonLayout.addWidget(DefiniteButton, 1, 0)
        ButtonLayout.addWidget(CancelButton, 1, 1)

        Layout = QVBoxLayout()
        Layout.addLayout(self.SelectFileLayout)
        Layout.addLayout(ButtonLayout)

        self.setLayout(Layout)

    def OnClickedSelectAll(self) -> None:
        self.SelectedFiles = {str(i):True for i in range(100)}
        self.SetButtonChecked(True)
    
    def OnClickedDeselectAll(self) -> None:
        self.Reset()

    def OnFileToggled(self, checked: bool) -> None:
        if checked:
            self.SelectedFiles[self.sender().text()] = True
        else:
            self.SelectedFiles.pop(self.sender().text())

    def OnClickedDefinite(self) -> Dict[str, bool]:
        self.BEGIN_CreateTerrainDelegate.emit(self.SelectedFiles)

    def OnClickedCancel(self) -> None:
        self.CANCEL_SelectFileDelegate.emit()
        self.close()
    
    def Reset(self) -> None:
        self.SetButtonChecked(False)
        self.SelectedFiles.clear()
    
    def SetButtonChecked(self, Checked: bool) -> None:
        KeysTemp = list(self.SelectedFiles.keys())
        for key in KeysTemp:
            _QWidgetObj = self.SelectFileLayout.itemAt(int(key)).widget()
            _QWidgetObj.setChecked(Checked)
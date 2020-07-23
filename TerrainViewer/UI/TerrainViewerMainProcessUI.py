# --- STL ---
import sys
from pathlib import Path

# --- PL ---
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, 
    QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt

# --- MyL ---
from MainProcess.LoadItemDataThread import LoadItemDataThread, Notifier
from UI.SelectFileUI import SelectFileUI

class TerrainViewerMainProcessUI(QWidget):
    def InitUI(self):
        CreateButton = QPushButton("Create")
        CreateButton.clicked.connect(self.OnClickedCreateTerrain)

        SaveButton = QPushButton("Save")
        SaveButton.clicked.connect(self.OnClickedSave)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(self.OnClickedExit)

        ButtonLayout = QVBoxLayout()
        ButtonLayout.addWidget(CreateButton)
        ButtonLayout.addWidget(ExitButton)

        UserInteractiveLayout = QVBoxLayout()
        UserInteractiveLayout.addWidget(self.ItemList)
        UserInteractiveLayout.addLayout(ButtonLayout)

        self.CanvasLayout = QVBoxLayout()
        self.CanvasLayout.addWidget(self.Canvas)
        self.CanvasLayout.addWidget(SaveButton)

        Layout = QHBoxLayout()
        Layout.addLayout(UserInteractiveLayout)
        Layout.addLayout(self.CanvasLayout)

        self.setLayout(Layout)

    def OnClickedCreateTerrain(self) -> None:
        self.LoadItemThreadNotifier = Notifier()
        self.LoadItemThread = LoadItemDataThread(
            self.LoadItemThreadNotifier, 
            self.ItemDirList[self.SelectedItemIndex]
        )
        self.LoadItemThreadNotifier.moveToThread(self.LoadItemThread)

        self.LoadItemThread.BEGIN_LoadDelegate.connect(self.OnBeginLoadItem)
        self.LoadItemThread.LoadLineDelegate.connect(self.OnLoadLine)
        self.LoadItemThread.FinishedLoopDelegate.connect(self.OnFinishedLoadItem)
        self.LoadItemThread.FIND_GridHighSizeDelegate.connect(self.OnFIND_GridHighSize)
        self.LoadItemThread.FIND_ElevDataDelegate.connect(self.OnFIND_ElevData)

        self.LoadItemThread.OnLoop()
        self.LoadItemThread.start()

    def OnClickedSave(self) -> None:
        try:
            if self.ItemImage:
                FileName, _ = QFileDialog.getSaveFileName(self, "Save", "", filter="*.png")
                self.ItemImage.save(FileName)
        except:
            QMessageBox.information(
                self,
                "Not Exist Image Error", 
                "Can't save not exist Image", 
                QMessageBox.Ok
            )
    
    def OnClickedExit(self) -> None:
        sys.exit()
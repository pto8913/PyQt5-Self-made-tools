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

class TerrainViewerMainProcessUI(QWidget):
    def InitUI(self):
        SaveButton = QPushButton("Save")
        SaveButton.clicked.connect(self.OnClickedSave)
        
        ExitButton = QPushButton("Exit")
        ExitButton.clicked.connect(self.OnClickedExit)

        ButtonLayout = QVBoxLayout()
        ButtonLayout.addWidget(ExitButton)

        self.ItemListTabWidget.addTab(self.ItemList, "ItemList")

        UserInteractiveLayout = QVBoxLayout()
        UserInteractiveLayout.addWidget(self.ItemListTabWidget)
        UserInteractiveLayout.addLayout(ButtonLayout)

        self.CanvasLayout = QVBoxLayout()
        self.CanvasLayout.addWidget(self.Canvas)
        self.CanvasLayout.addWidget(SaveButton)

        Layout = QHBoxLayout()
        Layout.addLayout(UserInteractiveLayout)
        Layout.addLayout(self.CanvasLayout)

        self.setLayout(Layout)

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
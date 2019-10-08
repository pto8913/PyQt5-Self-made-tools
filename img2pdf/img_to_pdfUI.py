from PyQt5.QtWidgets import (
  QWidget, QPushButton, QGridLayout, QMainWindow, QAction,
  QVBoxLayout, QFileDialog, QMessageBox, QInputDialog, QLineEdit, 
)

from PyQt5.QtCore import Qt

from pathlib import Path
import img2pdf

class MainUI(QMainWindow):
    def initUI(self):
        menubar = self.menuBar()
        
        saveAct = QAction("Save", self)
        saveAct.setShortcut("Ctrl+S")
        saveAct.triggered.connect(self.myLayout.clickedSave)

        exitAct = QAction("Exit", self)
        exitAct.setShortcut("Ctrl+Q")
        exitAct.triggered.connect(self.myLayout.clickedExit)

        openAct = QAction("Open", self)
        openAct.setShortcut("Ctrl+O")
        openAct.triggered.connect(self.myLayout.clickedAdd)

        resetAct = QAction("Reset", self)
        resetAct.triggered.connect(self.myLayout.clickedClear)

        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(resetAct)
        fileMenu.addAction(saveAct)
        fileMenu.addAction(openAct)
        fileMenu.addAction(exitAct)

        self.setGeometry(100, 100, 300, 400)

class LayoutUI(QWidget):
    def initUI(self):
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.clickedSave)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.clickedExit)

        addButton = QPushButton("Add Item")
        addButton.clicked.connect(self.clickedAdd)

        clearButton = QPushButton("Clear Item")
        clearButton.clicked.connect(self.clickedClear)

        deleteButton = QPushButton("Delete Item")
        deleteButton.clicked.connect(self.clickedDelete)

        sortButton = QPushButton("Sort Item")
        sortButton.clicked.connect(self.clickedSort)

        buttonLayout = QGridLayout()
        buttonLayout.addWidget(saveButton, 0, 0)
        buttonLayout.addWidget(clearButton, 0, 1)
        buttonLayout.addWidget(exitButton, 0, 2)
        buttonLayout.addWidget(addButton, 1, 0)
        buttonLayout.addWidget(deleteButton, 1, 1)
        buttonLayout.addWidget(sortButton, 1, 2)

        entireLayout = QVBoxLayout()
        entireLayout.addWidget(self.FileList)
        entireLayout.addLayout(buttonLayout)

        self.setLayout(entireLayout)

        
    def clickedAdd(self):
        FileName, ok = QFileDialog.getOpenFileNames(self, "Open", str(self.current_dir))
        if not ok:
            return 
        
        for f in FileName:
            x = Path(f)
            if x.suffix == self.Extension:
                self.FileList.addItem(x.name)
                self.ImagePathList.append(x)

    def clickedSave(self):
        filename, _ = QInputDialog.getText(
            self, 
            "Enter Filename", 
            "filename: ", 
            QLineEdit.Normal, 
            ""
        )
        if filename:
            if ".pdf" not in Path(filename).suffix:
                filename += ".pdf"
            path = self.current_dir.joinpath(filename)
            try:
                if path.exists():
                    QMessageBox.information(
                            self,
                            "Filename Error",
                            "This filename is already exists <br>\
                            Please change.\
                            ",
                            QMessageBox.Ok
                    )
                    return self.clickedSave()
                with open(path , "wb") as f:
                    f.write(img2pdf.convert(list(map(str, self.ImagePathList))))
                f.close()
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "WARNING", 
                    str(e) + 
                    "<br> PLEASE CHECK YOUR FILE FORMAT <br>\
                    THIS IS VERY VERY STRANGE SITUATION. <br>\
                    ",
                    QMessageBox.Ok
                )


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clickedExit()

    def clickedExit(self):
        exit()

    def clickedSort(self):
        self.ImagePathList = sorted(self.ImagePathList, key =  lambda x: x.name)
        self.FileList.sortItems()

    def clickedClear(self):
        self.ImagePathList = []
        self.FileList.clear()

    def clickedDelete(self):
        try:
            row = self.FileList.row(self.FileList.selectedItems()[0])
            self.ImagePathList.pop(row)
            self.FileList.takeItem(row)
        except:
            QMessageBox.information(
                self, 
                "No Item Error", 
                "Select delete item", 
                QMessageBox.Ok
            )

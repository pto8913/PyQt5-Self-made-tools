# ---- STL ----

# --- PL ---
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox

class TerrainViewerMainUI(QMainWindow):
    def InitUI(self) -> None:
        MenuBar = self.menuBar()

        SaveAct = QAction('&Save', self)
        SaveAct.setShortcut('Ctrl+S')
        SaveAct.triggered.connect(self.MainProcess.OnClickedSave)

        ExitAct = QAction('&Exit', self)
        ExitAct.setShortcut('Ctrl+Q')
        ExitAct.triggered.connect(self.MainProcess.OnClickedExit)

        FileMenu = MenuBar.addMenu('&File')
        FileMenu.addAction(SaveAct)
        FileMenu.addAction(ExitAct)

        HelpAct = QAction('Help', self)
        HelpAct.triggered.connect(self.ClickedHelp)

        HelpMenu = MenuBar.addMenu('&Help')
        HelpMenu.addAction(HelpAct)
        
        self.setGeometry(0, 0, 1000, 400)
        self.setWindowTitle("TerrainViewer")
        self.show()

    def ClickedHelp(self):
        QMessageBox.information(
            self,
            "Help", 
            """
                This is Help <br> 
                lat is latitude, lon is longitude. <br>
                Enter lat and lon by yourself or select from file list <br>
                if lat or lon is blank, you can't show map. <br>
                if you want to save figure press Ctrl+S or click Save Figure, <br> 
                but be careful Not exist figure can't save.
            """,
            QMessageBox.Ok
        )
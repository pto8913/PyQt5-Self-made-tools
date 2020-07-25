# --- STL ---
import sys

# --- PL ---
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QFont

# --- MyL ---
from UI.TerrainViewerMainUI import TerrainViewerMainUI
from MainProcess.TerrainViewerMainProcess import TerrainViewerMainProcess

class Main(TerrainViewerMainUI):
    def __init__(self) -> None:
        super(Main, self).__init__()
        self.MainProcess = TerrainViewerMainProcess()
        self.MainProcess.StatusMessageDelegate.connect(self.SetStatusMessage)
        self.setCentralWidget(self.MainProcess)
        self.InitUI()

    def SetStatusMessage(self, InMessage: str) -> None:
        self.statusBar().showMessage(InMessage)

def main():
    app = QApplication(sys.argv)
    font = QFont("Meiryo")
    app.setFont(font)
    w = Main()
    w.setWindowTitle("SQLiteViewer")
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()
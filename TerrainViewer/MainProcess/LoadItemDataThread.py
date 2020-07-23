# --- STL ---
import re

# --- PL ---
import numpy as np
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

class Notifier(QObject):
    notify = pyqtSignal()

class LoadItemDataThread(QThread):
    BEGIN_LoadDelegate = pyqtSignal()
    LoadLineDelegate = pyqtSignal(int)
    FIND_GridHighSizeDelegate = pyqtSignal(int, int)
    FIND_ElevDataDelegate = pyqtSignal(int, float)
    FinishedLoopDelegate = pyqtSignal()

    def __init__(self, notifier, InItemPath: str):
        super(LoadItemDataThread, self).__init__()

        self.Notifier = notifier

        # ファイルを読み込む際の正規表現たち
        self.GridLowPtn = re.compile(r"<gml:low>(.*) (.*)</gml:low>")
        self.GridHighPtn = re.compile(r"<gml:high>(.*) (.*)</gml:high>")
        self.ElevDataPtn = re.compile(r"(.*),(.*)")

        self.ItemPath = InItemPath
        self.isRunning = False

    def run(self) -> None:
        with open(self.ItemPath, encoding = "utf-8") as f:
            bIsFindedLow = False
            GridXLow = GridYLow = 0
            
            bIsFindedHigh = False
            GridXHigh = GridYHigh = 0

            ElevDataIdx = 0
            LoadLineCount = 0

            __Lines = f.readlines()
            self.BEGIN_LoadDelegate.emit()
            TotalLine = len(__Lines)
            for Line in __Lines:
                LoadLineCount += 1
                self.LoadLineDelegate.emit(int(LoadLineCount / TotalLine * 100))
                self.Notifier.notify.emit()
                if not bIsFindedLow:
                    __Match = re.search(self.GridLowPtn, Line)
                    if __Match:
                        GridXLow = int(__Match.groups()[0])
                        GridYLow = int(__Match.groups()[1])
                        bIsFindedLow = True
                
                if bIsFindedLow and not bIsFindedHigh:
                    __Match = re.search(self.GridHighPtn, Line)
                    if __Match:
                        GridXHigh = int(__Match.groups()[0])
                        GridYHigh = int(__Match.groups()[1])
                        bIsFindedHigh = True

                        self.FIND_GridHighSizeDelegate.emit(GridXHigh - GridXLow + 1,  GridYHigh - GridYLow + 1)
                
                if bIsFindedHigh:
                    __Match = re.search(self.ElevDataPtn, Line)
                    if __Match:
                        Elev = float(__Match.groups()[1])
                        self.FIND_ElevDataDelegate.emit(ElevDataIdx, Elev)
                        ElevDataIdx += 1
            self.FinishedLoopDelegate.emit()

    def OnLoop(self) -> None:
        self.isRunning = True
    
    def OffLoop(self) -> None:
        self.isRunning = False
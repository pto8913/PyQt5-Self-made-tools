# --- STL ---
import re
import queue
import time
from pathlib import Path

# --- PL ---
import numpy as np
from PyQt5.QtCore import (
    QObject, pyqtSignal, QRunnable, QCoreApplication
)

# --- MyL ---
from Templates.MyMath import Math
from Templates.MyStructs import LoadedItemData

MINIMUM_ELEV = -100

class Notifier(QObject):
    ReturnLoadedItemDataDelegate = pyqtSignal(LoadedItemData)
    ReturnTotalLineDelegate = pyqtSignal(int)
    ReturnLoadLine = pyqtSignal(int)

class LoadedItemDataThread(QRunnable):
    def __init__(
        self, 
        InNotifier, InQueue, 
        InItemPath: str, InPriorityIndex: int
    ):
        super(LoadedItemDataThread, self).__init__()
    
        self.Notifier = InNotifier
        self.TaskQueue = InQueue
        
        self.LoadedItemData = LoadedItemData()
        self.LoadedItemData.ItemPath = InItemPath
        self.LoadedItemData.ItemNum = Path(InItemPath).name.split("-")[4]

        self.LoadedItemData.ItemPriority = InPriorityIndex
        
        # ファイルを読み込む際の正規表現たち
        self.GridLowPtn = re.compile(r"<gml:low>(.*) (.*)</gml:low>")
        self.GridHighPtn = re.compile(r"<gml:high>(.*) (.*)</gml:high>")
        self.ElevDataPtn = re.compile(r"(.*),(.*)")

        self.MinimumElev = 0

        self.ItemPath = InItemPath

    def run(self) -> None:
        # app = QCoreApplication.instance()
        with open(self.ItemPath, encoding="utf-8") as f:
            print(f)
            bIsFindedLow = False
            bIsFindedHigh = False
            ElevDataIdx = 0
            LoadLineCount = 0

            __Lines = f.readlines()
            TotalLine = len(__Lines)
            self.Notifier.ReturnTotalLineDelegate.emit(TotalLine)
            for Line in __Lines:
                LoadLineCount += 1
                self.Notifier.ReturnLoadLine.emit(LoadLineCount)
                if not bIsFindedLow:
                    __Match = re.search(self.GridLowPtn, Line)
                    if __Match:
                        bIsFindedLow = True
                        self.LoadedItemData.GridXLow = int(__Match.groups()[0])
                        self.LoadedItemData.GridYLow = int(__Match.groups()[1])
                
                if bIsFindedLow and not bIsFindedHigh:
                    __Match = re.search(self.GridHighPtn, Line)
                    if __Match:
                        self.LoadedItemData.GridXHigh = int(__Match.groups()[0])
                        self.LoadedItemData.GridYHigh = int(__Match.groups()[1])
                        bIsFindedHigh = True

                        self.LoadedItemData.InitElev()
                
                if bIsFindedHigh:
                    __Match = re.search(self.ElevDataPtn, Line)
                    if __Match:
                        Elev = float(__Match.groups()[1])
                        if not isinstance(Elev, float):
                            Elev = MINIMUM_ELEV
                        else:
                            if Elev < self.MinimumElev:
                                if MINIMUM_ELEV < Elev:
                                    self.MinimumElev = Elev
                        Elev = Math.clamp(Elev, MINIMUM_ELEV, 9999.0) + 32768
                        self.LoadedItemData.AddElev(ElevDataIdx, Elev)
                        ElevDataIdx += 1
        
        self.LoadedItemData.MinimumElev = self.MinimumElev
        self.Notifier.ReturnLoadedItemDataDelegate.emit(self.LoadedItemData)
        
        time.sleep(0.01) 
        # app.quit()
        self.TaskQueue.task_done()

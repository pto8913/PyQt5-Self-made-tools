# --- STL ---
import re
import time
from pathlib import Path

# --- PL ---
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

# --- MyL ---
from Templates.MyMath import Math
from Templates.MyStructs import LoadedItemData

MINIMUM_ELEV = -100

class LoadedItemDataThread(QObject):
    ReturnLoadedItemDataDelegate = pyqtSignal(int, LoadedItemData)
    ReturnTotalLineDelegate = pyqtSignal(int)
    ReturnLoadLine = pyqtSignal(int)

    def __init__(self, InItemPath: str):
        super(LoadedItemDataThread, self).__init__()
    
        self.LoadedItemData = LoadedItemData()
        self.LoadedItemData.ItemPath = InItemPath
        self.ItemNum = int(Path(InItemPath).name.split("-")[4])

        # ファイルを読み込む際の正規表現たち
        self.ElevDataPtn = re.compile(r"(.*),(.*)")

        self.MinimumElev = 0

        self.ItemPath = InItemPath

    @pyqtSlot()
    def BeginLoadItemData(self) -> None:
        with open(self.ItemPath, encoding="utf-8") as f:
            ElevDataIdx = 0
            LoadLineCount = 0

            __Lines = f.readlines()
            TotalLine = len(__Lines)
            self.ReturnTotalLineDelegate.emit(TotalLine)
            for Line in __Lines:
                LoadLineCount += 1
                self.ReturnLoadLine.emit(LoadLineCount / TotalLine * 100)
                
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
        self.ReturnLoadedItemDataDelegate.emit(self.ItemNum, self.LoadedItemData)
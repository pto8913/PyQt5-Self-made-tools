# --- STL ---
from typing import Dict, List, Tuple

# --- PL ---
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

# --- MyL ---
from Templates.MyMath import Math

"""
    DFSで隣接するファイルを探してブロックにまとめ、画像を繋げて出力できるようにする

    例えば、
    
    [[(0, 0), (0, 1), (1, 0)],[(9, 9)]]
    
    の配列を

    [[0 1],
    [1 -1]]

    [9]
    
    のようにする

    ※ -1 : データなし
"""

class ItemImageJoinableTileSearch(QObject):
    JoinableTilesDelegate = pyqtSignal(object)

    def __init__(self, InUserSelectedItems: Dict[str, bool]):
        super(ItemImageJoinableTileSearch, self).__init__()

        self.UserSelectedItems = [[False for _ in range(10)] for _ in range(10)]
        self.DFSReached = [[False for _ in range(10)] for _ in range(10)]

        for key in InUserSelectedItems.keys():
            key = int(key)
            self.UserSelectedItems[key // 10][key % 10] = True
        
        self.JoinableTileList = []
        self.__JoinableTileTemp = []

    @pyqtSlot()
    def DFS(self, x: int, y: int) -> None:
        if x < 0 or y < 0 or x >= 10 or y >= 10 or not self.UserSelectedItems[y][x]:
            return
        if self.DFSReached[y][x]:
            return
        self.DFSReached[y][x] = True
        self.__JoinableTileTemp.append((y, x))
        return self.DFS(x + 1, y) or self.DFS(x - 1, y) or self.DFS(x, y + 1) or self.DFS(x, y - 1)

    def BeginSearch(self) -> None:
        for y in range(10):
            for x in range(10):
                if self.UserSelectedItems[y][x] and not self.DFSReached[y][x]:
                    self.DFS(x, y)
                    self.JoinableTileList.append(self.__JoinableTileTemp)
                    self.__JoinableTileTemp = []
        
        # self.JoinableTilesDelegate.emit(self.JoinableTileList)
        self.RemakeTiles()

    def RemakeTiles(self) -> None:
        INF = int(1e9+7)
        self.RemakedTiles = []
        for Tiles in self.JoinableTileList:
            MinX, MinY = INF, INF
            MaxX, MaxY = 0, 0
            RemakeTiles = np.array([])
            if len(Tiles) > 1:
                for y, x in Tiles:
                    MinX = min(MinX, x)
                    MinY = min(MinY, y)
                    MaxX = max(MaxX, x)
                    MaxY = max(MaxY, y)
                RemakeTiles = np.full((MaxY - MinY + 1, MaxX - MinX + 1), -1)
                for y, x in Tiles:
                    ny, nx = y, x
                    if MinX != 0:
                        nx -= MaxX + 1
                    if MinY != 0:
                        ny -= MaxY + 1
                    RemakeTiles[ny][nx] = y * 10 + x
            else:
                RemakeTiles = np.array([Tiles[0][0] * 10 + Tiles[0][1]])
                MinX, MinY = 0, 0
            self.RemakedTiles.append(RemakeTiles)
        self.JoinableTilesDelegate.emit(self.RemakedTiles)
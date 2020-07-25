# --- STL ---
from pathlib import Path
import sys
import re
import queue
from typing import Dict, List, Tuple

# --- PL ---
import numpy as np
import matplotlib.cm as cmap
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QListWidget, QTabWidget, QTabWidget, 
    QLabel, QProgressBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal

# --- MyL ---
from UI.TerrainViewerMainProcessUI import TerrainViewerMainProcessUI
from SubProcesses.__LoadItemDataThread import LoadedItemDataThread
from SubProcesses.ItemImageJoinableTileSearch import ItemImageJoinableTileSearch
from UI.SelectFileUI import SelectFileUI
from Templates.MyStructs import LoadedItemData

class TerrainViewerMainProcess(TerrainViewerMainProcessUI):
    StatusMessageDelegate = pyqtSignal(str)

    def __init__(self) -> None:
        super(TerrainViewerMainProcess, self).__init__()

        # ファイルの名前をみるようのリスト
        self.ItemList = QListWidget()
        self.ItemList.setMinimumSize(200, 500)
        
        self.SelectedItemIndex = 0
        self.ItemList.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        self.ItemList.itemDoubleClicked.connect(self.OnItemDoubleClicked)
        
        self.ItemListTabWidget = QTabWidget()
        self.SelectFile = SelectFileUI(100)
        self.SelectFile.CANCEL_SelectFileDelegate.connect(self.OnCloseSelectFileTab)
        self.SelectFile.BEGIN_CreateTerrainDelegate.connect(self.OnCreateTerrainThread)

        # ファイルがあるディレクトリ
        self.ItemDirList = []

        self.CurrentDir = Path().cwd()
        self.SetItemList()
        
        self.Canvas = QLabel(u"ここに地形図が表示されます")
        self.Canvas.setScaledContents(True)
        self.Canvas.setMinimumSize(500, 400)

        self.LoadItemDataThread = QThread()
        self.LoadProgressBar = QProgressBar()
        self.LoadItemTasks = queue.Queue()
        self.LoadedItemDatas = {}

        self.ItemImageJoinableTileSearchThread = QThread()
        self.ItemImageJoinableTiles = []
        
        self.InitUI()

    # -------------- Init --------------
    def SetItemList(self) -> None:
        # for ItemPath in self.CurrentDir.glob("**/*.xml"):
        for ItemPath in [p for p in self.CurrentDir.glob("**/*") if re.search(r"FG-GML-(.*)-(.*)-DEM(.*)", str(p))]:
            if not str(ItemPath.suffix):
                self.ItemDirList.append(str(ItemPath))
                self.ItemList.addItem(str(ItemPath.name))

    # -------------- select file -------------
    def OnCloseSelectFileTab(self) -> None:
        self.ForceQuitTaskThread()
        self.ItemListTabWidget.removeTab(1)

    # -------------- user action --------------
    def OnItemSelectionChanged(self) -> None:
        self.SelectedItemIndex = self.ItemList.selectedIndexes()[0].row()
        self.CurrentDir = Path(self.ItemDirList[self.SelectedItemIndex])

    def OnItemDoubleClicked(self, item) -> None:
        if self.ItemListTabWidget.count() > 1:
            self.ItemListTabWidget.removeTab(1)
        self.SelectFile.Reset()
        self.ItemListTabWidget.addTab(self.SelectFile, "SelectFiles")
        self.ItemListTabWidget.setCurrentIndex(1)

    # -------------- UI action --------------
    # ファイルの一行が読み込まれるたびにプログレスバーを更新
    def OnUpdateLoadProgressBar(self, LoadItemProgress: int) -> None:
        self.LoadProgressBar.setValue(LoadItemProgress)

    # -------------- create terrain --------------
    def OnCreateTerrainThread(self, InFiles: Dict[str, bool]) -> None:
        if InFiles == {}:
            return
        # 選択されたファイルを繋げられるようにブロックごとにまとめる
        self.BeginItemImageJoinableTileSearch(InFiles)

        self.LoadedItemDatas = {}
        # 読み込みを始めたら、プログレスバーを表示する
        self.CanvasLayout.addWidget(self.LoadProgressBar)

        # ロードするタスクをキューに詰める
        for path in self.CurrentDir.glob("**/*.xml"):
            path_temp = path.name.split("-")
            if path_temp[4] in InFiles:
                self.LoadItemTasks.put(path)
        self.OnCallNextLoadItemDataTask()

    def CreateTerrainImage(self, Elev) -> None:
        self.ConvertndarrayToImage(Elev)

        w, h = self.FigureCanvas.get_width_height()
        self.ItemImage = QImage(
            self.FigureCanvas.buffer_rgba(), w, h, QImage.Format_ARGB32
        )
        self.Canvas.setPixmap(QPixmap(self.ItemImage))
    
    def ConvertndarrayToImage(self, In2darray: np.ndarray) -> None:
        plt.close()
        fig, ax = plt.subplots()
        # ls = LightSource(azdeg = 180, altdeg = 65)
        # color = ls.shade(self.ElevDatas, plt.get_cmap("rainbow_r"))
        # cs = ax.imshow(self.ElevDatas, plt.get_cmap("rainbow_r"))
        # color = ls.shade(self.ElevDatas, plt.get_cmap("gray"))
        cs = ax.imshow(In2darray, plt.get_cmap("gray"))
        # ax.imshow(color)

        # make_axes = make_axes_locatable(ax)
        # cax = make_axes.append_axes("right", size = "2%", pad = 0.05)
        # fig.colorbar(cs, cax)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
        
        self.FigureCanvas = FigureCanvas(fig)
        self.FigureCanvas.draw()
    
    # -------------- Load Select Item Data --------------
    def OnCallNextLoadItemDataTask(self) -> None:
        if self.LoadItemTasks.qsize() <= 0:
            print("Finished LoadTask")
            self.FinishedLoadItemDataTask()
            return
        else:
            # プログレスバーを0％にする
            self.LoadProgressBar.setValue(0)
            self.ForceQuitLoadItemDataTaskThread()
            path = self.LoadItemTasks.get()
            self.StatusMessageDelegate.emit(f"Now Loading {path}")
            self.LoadItemData = LoadedItemDataThread(path)

            self.LoadItemData.ReturnLoadedItemDataDelegate.connect(self.OnGetLoadedItemData)
            self.LoadItemData.ReturnLoadLine.connect(self.OnUpdateLoadProgressBar)
            self.LoadItemData.moveToThread(self.LoadItemDataThread)
            self.LoadItemDataThread.started.connect(self.LoadItemData.BeginLoadItemData)
            
            self.LoadItemDataThread.start()
    
    def OnGetLoadedItemData(self, ItemNum: int, LoadedItemDatas: LoadedItemData) -> None:
        self.LoadedItemDatas[ItemNum] = LoadedItemDatas
        self.OnCallNextLoadItemDataTask()

    def ForceQuitLoadItemDataTaskThread(self) -> None:
        if self.LoadItemDataThread.isRunning():
            self.LoadItemDataThread.terminate()
            self.LoadItemDataThread.wait()
        
    def FinishedLoadItemDataTask(self) -> None:
        self.ItemImageArraysList = []
        for Tiles in self.ItemImageJoinableTiles:
            vTemp = np.array([])

            ResultName = ""
            for Tile in Tiles:
                ResultName += str(Tile)
                if not isinstance(Tile, np.ndarray):
                    vTemp = self.LoadedItemDatas[Tile].Reshape()
                else:
                    hTemp = np.array([])
                    for elem in Tile:
                        temp = self.MakeEmptyImage()
                        if elem != -1:
                            temp = self.LoadedItemDatas[elem].Reshape()

                        if not len(hTemp):
                            hTemp = temp
                        else:
                            hTemp = np.hstack((hTemp, temp))
                    if not len(vTemp):
                        vTemp = hTemp
                    else:
                        vTemp = np.vstack((hTemp, vTemp))

            self.ItemImageArraysList.append(vTemp)
            self.ConvertndarrayToImage(vTemp)
            plt.savefig(f"{self.CurrentDir}-{ResultName}.png")
        print(self.ItemImageArraysList)

        # プログレスバーを非表示にする
        self.LoadProgressBar.setParent(None)   

    # -------------- Joinable Image Search --------------
    # 選択されたファイルを繋げられるようにブロックごとにまとめる
    def BeginItemImageJoinableTileSearch(self, InFiles: Dict[str, bool]) -> None:
        self.ForceQuitItemImageJoinableTileSearchThread()
        self.ItemImageJoinableTileSearch = ItemImageJoinableTileSearch(InFiles)
        self.ItemImageJoinableTileSearch.JoinableTilesDelegate.connect(self.OnGetJoinableTiles)
        self.ItemImageJoinableTileSearch.moveToThread(self.ItemImageJoinableTileSearchThread)
        self.ItemImageJoinableTileSearchThread.started.connect(self.ItemImageJoinableTileSearch.BeginSearch)
        self.ItemImageJoinableTileSearchThread.start()

    def ForceQuitItemImageJoinableTileSearchThread(self) -> None:
        if self.ItemImageJoinableTileSearchThread.isRunning():
            self.ItemImageJoinableTileSearchThread.terminate()
            self.ItemImageJoinableTileSearchThread.wait()

    def OnGetJoinableTiles(self, InTiles: List[np.ndarray]) -> None:
        self.ItemImageJoinableTiles = InTiles
    
    def MakeEmptyImage(self) -> np.ndarray:
        return np.full((150, 225), 32768)

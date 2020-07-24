# --- STL ---
from pathlib import Path
import sys
import re
import queue
from typing import Dict

# --- PL ---
import cv2
from PIL import Image
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
from PyQt5.QtCore import QThreadPool, QThread

# --- MyL ---
from UI.TerrainViewerMainProcessUI import TerrainViewerMainProcessUI
from MainProcess.__LoadItemDataThread import LoadedItemDataThread
from UI.SelectFileUI import SelectFileUI
from Templates.MyStructs import LoadedItemData
   
MINIMUM_ELEV = -100
MAX_THREADS = 4

class TerrainViewerMainProcess(TerrainViewerMainProcessUI):
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
        self.ItemDatas = []
        
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

    # -------------- create terrain --------------
    def OnCreateTerrainThread(self, InFiles: Dict[str, bool]) -> None:
        if InFiles == {}:
            return
        self.ItemDatas = []
        # 読み込みを始めたら、プログレスバーを表示する
        self.CanvasLayout.addWidget(self.LoadProgressBar)

        # ロードするタスクをキューに詰める
        for i, path in enumerate(self.CurrentDir.glob("**/*.xml")):
            path_temp = path.name.split("-")
            if path_temp[4] in InFiles:
                self.LoadItemTasks.put((path, i))
        self.OnCallNextTask()
    
    def OnCallNextTask(self) -> None:
        if self.LoadItemTasks.qsize() <= 0:
            print("Finished LoadTask")
            self.FinishedLoadTask()
            return
        else:
            # プログレスバーを0％にする
            self.LoadProgressBar.setValue(0)
            self.ForceQuitTaskThread()
            path, i = self.LoadItemTasks.get()
            print(f"Begin {path}")
            self.obj = LoadedItemDataThread(path, i)

            self.obj.ReturnLoadedItemDataDelegate.connect(self.OnGetLoadedItemData)
            self.obj.ReturnLoadLine.connect(self.OnUpdateLoadProgressBar)
            self.obj.FinishedDelegate.connect(self.OnCallNextTask)
            self.obj.moveToThread(self.LoadItemDataThread)
            self.LoadItemDataThread.started.connect(self.obj.LoadItemData)
            
            self.LoadItemDataThread.start()

    def ForceQuitTaskThread(self) -> None:
        if self.LoadItemDataThread.isRunning():
            self.LoadItemDataThread.terminate()
            self.LoadItemDataThread.wait()
    
    # ファイルの一行が読み込まれるたびにプログレスバーを更新
    def OnUpdateLoadProgressBar(self, LoadItemProgress: int) -> None:
        self.LoadProgressBar.setValue(LoadItemProgress)

    def OnGetLoadedItemData(self, LoadedItemDatas: LoadedItemData) -> None:
        self.ItemDatas.append(LoadedItemDatas)

    def FinishedLoadTask(self) -> None:
        for ItemData in self.ItemDatas:
            print(ItemData.ItemNum)
            ItemData2D = ItemData.Reshape()
            
            self.ConvertndarrayToImage(ItemData2D)

            plt.savefig(str(self.CurrentDir) + f"-{ItemData.ItemNum}.png")
            print(str(self.CurrentDir) + f"-{ItemData.ItemNum}.png")
        print("Finished Save All Figure")

        self.CreateTerrainImage(self.ItemDatas[0].Reshape())

        # プログレスバーを非表示にする
        self.LoadProgressBar.setParent(None)   

    def CreateTerrainImage(self, Elev):
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
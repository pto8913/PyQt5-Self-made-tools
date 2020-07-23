# --- STL ---
from pathlib import Path
import sys
import re

# --- PL ---
import numpy as np
import matplotlib.cm as cmap
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QListWidget,
    QLabel, QProgressBar
)
from PyQt5.QtGui import QPixmap, QImage

# --- MyL ---
from UI.TerrainViewerMainProcessUI import TerrainViewerMainProcessUI
from Math.mymath import Math
   
MINIMUM_ELEV = -100

class TerrainViewerMainProcess(TerrainViewerMainProcessUI):
    def __init__(self) -> None:
        super(TerrainViewerMainProcess, self).__init__()

        # ファイルの名前をみるようのリスト
        self.ItemList = QListWidget()
        self.ItemList.setMinimumSize(200, 500)
        
        self.SelectedItemIndex = 0
        self.ItemList.itemSelectionChanged.connect(self.OnItemSelectionChanged)
        self.ItemList.itemDoubleClicked.connect(self.OnItemDoubleClicked)

        # ファイルがあるディレクトリ
        self.ItemDirList = []

        self.CurrentDir = Path().cwd()
        self.SetItemList()
        
        self.Canvas = QLabel(u"ここに地形図が表示されます")
        self.Canvas.setScaledContents(True)
        self.Canvas.setMinimumSize(500, 400)

        self.LoadProgressBar = QProgressBar()

        self.MinimumElev = 0
        
        self.InitUI()

    def closeEvent(self, event) -> None:
        self.SelectFile.OnClickedCancel()

    def OnItemSelectionChanged(self) -> None:
        self.SelectedItemIndex = self.ItemList.selectedIndexes()[0].row()

    # 読み込みを始めたら、プログレスバーを表示する
    def OnBeginLoadItem(self) -> None:
        self.CanvasLayout.addWidget(self.LoadProgressBar)
        self.LoadProgressBar.setValue(0)

    # ファイルの一行が読み込まれるたびにプログレスバーを更新
    def OnLoadLine(self, LoadItemProgress: int) -> None:
        self.LoadProgressBar.setValue(LoadItemProgress)
        
    def OnFinishedLoadItem(self) -> None:
        self.LoadItemThread.OffLoop()
        self.LoadItemThread.quit()
        self.LoadItemThread.wait()
        # プログレスバーを非表示にする
        self.LoadProgressBar.setParent(None)
        self.CreateTerrainImage()
    
    def OnFIND_GridHighSize(self, SizeX: int, SizeY: int) -> None:
        self.GridXSize = SizeX
        self.GridYSize = SizeY
        self.ElevDatas = np.zeros(SizeX * SizeY, dtype=np.uint16)

    def OnFIND_ElevData(self, ElevDataIndex: int, Elev: float) -> None:
        if not isinstance(Elev, float):
            Elev = MINIMUM_ELEV
        else:
            if Elev < self.MinimumElev:
                if MINIMUM_ELEV < Elev:
                    self.MinimumElev = Elev
        Elev = Math.clamp(Elev, MINIMUM_ELEV, 9999.0)
        self.ElevDatas[ElevDataIndex] = Elev + 32768

    def CreateTerrainImage(self):
        plt.close()

        self.ElevDatas = self.ElevDatas.reshape((self.GridYSize, self.GridXSize))
        self.ElevDatas = np.where(self.ElevDatas <= MINIMUM_ELEV, self.MinimumElev, self.ElevDatas)

        fig, ax = plt.subplots()
        # ls = LightSource(azdeg = 180, altdeg = 65)
        # color = ls.shade(self.ElevDatas, plt.get_cmap("rainbow_r"))
        # cs = ax.imshow(self.ElevDatas, plt.get_cmap("rainbow_r"))
        # color = ls.shade(self.ElevDatas, plt.get_cmap("gray"))
        cs = ax.imshow(self.ElevDatas, plt.get_cmap("gray"))
        # ax.imshow(color)

        # make_axes = make_axes_locatable(ax)
        # cax = make_axes.append_axes("right", size = "2%", pad = 0.05)
        # fig.colorbar(cs, cax)

        ax.set_xticks([])
        ax.set_yticks([])
        fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
        
        canvas = FigureCanvas(fig)
        canvas.draw()

        w, h = canvas.get_width_height()
        self.ItemImage = QImage(
            canvas.buffer_rgba(), w, h, QImage.Format_ARGB32
        )
        self.Canvas.setPixmap(QPixmap(self.ItemImage))

    def SetItemList(self) -> None:
        # for ItemPath in self.CurrentDir.glob("**/*.xml"):
        for ItemPath in [p for p in self.CurrentDir.glob("**/*") if re.search(r"FG-GML-(.*)-(.*)-DEM(.*)", str(p))]:
            if not str(ItemPath.suffix):
                self.ItemDirList.append(str(ItemPath))
                self.ItemList.addItem(str(ItemPath.name))

    def OnItemDoubleClicked(self, item) -> None:        
        self.SelectFile.setWindowTitle(item.text())
        self.SelectFile.show()
        self.SelectFile.raise_()
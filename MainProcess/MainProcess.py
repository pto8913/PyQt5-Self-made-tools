from Thread.MusicTearOffThread import MusicTearOff
from UI.MainProcessUI import MainProcessUI

from PyQt5.QtWidgets import QProgressBar, QFileDialog
from PyQt5.QtCore import QThread

from pathlib import Path
import sqlite3
import numpy as np
import cv2

extensions = [".avi", ".mp4"]

"""
def FinishedMusicTearOff(self):
    Capture = cv2.VideoCapture(str(self.CurrentVideoPath))
    _, VideoData = Capture.read()

Capture.read()の部分でデータを全部取得するのかと思ったけど、1フレームのデータを返すので、この方法は良くない。

"""

class MainProcess(MainProcessUI):
    def __init__(self):
        super(MainProcess, self).__init__()
        self.setAcceptDrops(True)

        self.ItemPathList = []

        self.CurrentPath = Path().cwd()
        if not Path(f"{self.CurrentPath}/SaveVideo").exists():
            Path(f"{self.CurrentPath}/SaveVideo").mkdir()
        
        self.OutPutPath = f"{self.CurrentPath}/SaveVideo"

        self.MusicTearOffThread = QThread()

        self.InitUI()

    def OnClickedStart(self):
        self.RenameFile()

        self.DBName = self.DBNameLine.text()
        print(self.DBName)
        if self.DBName == '' or self.DBName == 'DBName':
            self.DBName = "SaveVideo.db"
        else:
            if Path(self.DBName).suffix == '':
                self.DBNameLine += ".db"

        self.conn = sqlite3.connect(
            f"{str(self.CurrentPath)}/{self.DBName}"
        )
        self.cur = self.conn.cursor()
        
        self.TableName = self.TableNameLine.text()
        if self.TableName == 'TableName' or self.TableName == '':
            self.TableName = "SaveVideo"
        print(self.TableName)
        sql = f"CREATE TABLE IF NOT EXISTS {self.TableName}(Name TEXT, VideoData BLOB, VideoShapeY int, VideoShapeX int, MusicData BLOB, MusicShapeY int, MusicShapeX int)"
        self.cur.execute(sql)
        self.conn.commit()

        self.NumOfItem = len(self.ItemPathList)
        self.CurrentLoadItemIdx = 0

        self.ProgressBar = QProgressBar()
        self.Layout.addWidget(self.ProgressBar)

        self.__Start(self.CurrentLoadItemIdx)

    def __Start(self, Idx: int):
        print(Idx)
        self.ForceQuitMusicTearOffThread()

        self.ProgressBar.setValue( Idx / self.NumOfItem )

        self.CurrentVideoPath = self.ItemPathList[Idx]

        self.MusicTearOff = MusicTearOff(
            self.CurrentVideoPath,
            self.OutPutPath
        )
        self.MusicTearOff.FinishedDelegate.connect(self.FinishedMusicTearOff)
        self.MusicTearOff.FailedDelegate.connect(self.AddFailedList)
        
        self.MusicTearOff.moveToThread(self.MusicTearOffThread)
        self.MusicTearOffThread.started.connect(self.MusicTearOff.Start)
        self.MusicTearOffThread.start()
    
    def ForceQuitMusicTearOffThread(self):
        if self.MusicTearOffThread.isRunning():
            self.MusicTearOffThread.terminate()
            self.MusicTearOffThread.wait()

    def FinishedMusicTearOff(self, MusicData: np.ndarray):
        print("Finished")

        Capture = cv2.VideoCapture(str(self.CurrentVideoPath))
        _, VideoData = Capture.read()

        print(self.TableName)
        print(self.CurrentVideoPath)

        print(VideoData)
        print(VideoData.shape)

        print(MusicData)
        print(MusicData.shape)

        self.cur.execute(f"INSERT INTO {self.TableName} (Name, VideoData, VideoShapeY, VideoShapeX, MusicData, MusicShapeY, MusicShapeX) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.CurrentVideoPath.name.split('.')[0], VideoData, VideoData.shape[0], VideoData.shape[1], MusicData, MusicData.shape[0], MusicData.shape[1])
        )
        self.conn.commit()

        Path(f"{self.OutPutPath}/{Path(self.CurrentVideoPath).name.split('.')[0]}.wav").unlink()
        self.CheckStart()

    def OnClickedAddFile(self):
        files = QFileDialog.getOpenFileNames(
            self, "Open File", self.CurrentPath, "Video Files(*.mp4, *.avi)"
        )
        for e in files:
            self.FileWidget.addItem(e)
    
    def RenameFile(self):
        for idx, elem in enumerate(self.ItemPathList):
            res = str(elem).split()
            if len(res) != 1:
                newpath = self.IsExist(res[0] + ".mp4")
                self.ItemPathList[idx] = newpath
                elem.rename(newpath)

    def IsExist(self, InPath):
        if Path(InPath).exists():
            newpath = str(InPath).split(".")[0] + "(1).mp4"
            return self.IsExist(Path(newpath))
        else:
            return Path(InPath)

    def AddFailedList(self, InPath):
        self.FailedItemList.addItem(InPath)
        self.CheckStart()

    
    def CheckStart(self):
        if self.CurrentLoadItemIdx < self.NumOfItem:
            self.CurrentLoadItemIdx += 1
            self.__Start(self.CurrentLoadItemIdx)
        else:
            self.ProgressBar.setParent(None)
    
    # ---------------- FileWidget on drop event ----------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = Path(url.toLocalFile())
            if path.is_dir():
                self.AddDir(path)
            else:
                self.FileWidget.addItem(path.name)
                self.ItemPathList.append(path)
    
    def AddDir(self, InPath):
        for elem in InPath.glob("**/*"):
            if elem.suffix in extensions:
                self.FileWidget.addItem(elem.name)
                self.ItemPathList.append(elem)

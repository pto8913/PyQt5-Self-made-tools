import sys
import re
import pygame
from pathlib import Path
from PyQt5.QtWidgets import (
  QApplication, QListWidget,
)
from PyQt5.QtGui import QFont

from MusicPlayerUI import MusicPlayerUI

class MusicPlayer(MusicPlayerUI):
    def __init__(self, parent = None):
        super(MusicPlayer, self).__init__(parent)
        pygame.init()

        self.index = 0
        self.music = pygame.mixer.music

        self.setAcceptDrops(True)

        self.PathInit()
        self.pause = True
        self.loop = False

        self.FileList = QListWidget(self)
        self.FilePathList = []
        self.setFileList()
        self.FileList.itemSelectionChanged.connect(self.FileListChanged)
        self.fileName = ""
        
        self.initUI()

    def clickedExit(self):
        sys.exit()

    def loopMusic(self):
        if self.loop:
            self.loopButton.setText("Loop?")
            self.loop = False
        else:
            self.loopButton.setText("Loop")  
            self.loop = True

    def startMusic(self):
        try:
            row = self.FileList.row(self.FileList.selectedItems()[0])
        except:
            return
        self.music.load(str(self.FilePathList[row]))
        self.music.play(1)
        self.isPause()
        if self.loop:
            self.resetMusic()
            return
        PLAY_END = pygame.USEREVENT+1
        self.music.set_endevent(PLAY_END)
        tmp = True
        while tmp:
            for event in pygame.event.get():
                if event.type == PLAY_END:
                    self.checkNext()
                    tmp = False
                    break
        self.startMusic()

    def setFileList(self):
        for item in [f for f in self.music_dir.glob("**/*") if re.search(r".+\.(mp3|m4a)", f.name)]:
            self.FileList.addItem(item.name)
            self.FilePathList.append(item)

    def FileListChanged(self):
        self.fileName = self.FileList.selectedItems()[0].text()
        self.startMusic()

    def nextMusic(self):
        if self.loop:
            self.resetMusic()
            return
        self.isPause()
        self.checkNext()
        self.startMusic()

    def checkNext(self):
        if self.index+1 < len(self.FileList):
            self.index += 1
        else:
            self.index = 0
        self.fileName = self.FileList.item(self.index).text()

    def pauseMusic(self):
        if self.pause:
            self.music.pause()
            self.pauseButton.setText("Clicked Pause")
            self.pause = False
        else:
            self.music.unpause()
            self.isPause()

    def isPause(self):
        if not self.pause:
            self.pause = True
            self.pauseButton.setText("Pause?")

    def resetMusic(self):
        self.music.rewind()

    def PathInit(self):
        self.music_dir = Path().home().joinpath("music")

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = MusicPlayer()
    w.setWindowTitle('Music Player')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()
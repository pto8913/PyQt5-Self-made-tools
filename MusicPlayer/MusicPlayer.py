import sys
import re
import pygame
from pathlib import Path
from PyQt5.QtWidgets import (
  QApplication, QListWidget,
)
from PyQt5.QtGui import QFont

import sqlite3

from MusicPlayerUI import MusicPlayerUI

class MusicPlayer(MusicPlayerUI):
    def __init__(self, parent = None):
        super(MusicPlayer, self).__init__(parent)
        pygame.init()

        self.music = pygame.mixer.music

        self.setAcceptDrops(True)

        self.PathInit()
        self.pause = False
        self.loop = False

        self.row = 0

        self.music_list = QListWidget(self)
        self.music_path_list = []
        self.setMusicList()
        self.music_list.itemSelectionChanged.connect(self.setMusic)
        self.music_name = ""
        
        self.initUI()


    def isPause(self):
        if self.pause:
            self.pause = False
            self.pauseButton.setText("Pause?")


    def setMusic(self):
        self.row = self.music_list.row(self.music_list.selectedItems()[0])
        self.startMusic()

    # ---------------------------- Init ---------------------------

    def PathInit(self):
        self.music_dir = Path().home().joinpath("music")


    def setMusicList(self):
        for item in self.music_dir.glob("**/*.mp3"):
            self.music_list.addItem(item.name)
            self.music_path_list.append(item)


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
from PyQt5.QtWidgets import (
  QWidget, QGridLayout, QPushButton, QVBoxLayout
)
import sys
import re
import pygame

from pathlib import Path

class MusicPlayerUI(QWidget):
    def initUI(self):
        startButton = QPushButton("Start")
        startButton.clicked.connect(self.startMusic)

        self.pauseButton = QPushButton("Pause?")
        self.pauseButton.clicked.connect(self.pauseMusic)

        nextButton = QPushButton("Next")
        nextButton.clicked.connect(self.nextMusic)

        self.loopButton = QPushButton("Loop?")
        self.loopButton.clicked.connect(self.loopMusic)
        
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.restartMusic)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.clickedExit)

        buttonlayout = QGridLayout()
        buttonlayout.addWidget(startButton, 0, 0)
        buttonlayout.addWidget(self.pauseButton, 0, 1)
        buttonlayout.addWidget(nextButton, 0, 2)
        buttonlayout.addWidget(self.loopButton, 1, 0)
        buttonlayout.addWidget(resetButton, 1, 1)
        buttonlayout.addWidget(exitButton, 1, 2)

        layout = QVBoxLayout()
        layout.addWidget(self.music_list)
        layout.addLayout(buttonlayout)
        
        self.setLayout(layout)

        self.setGeometry(300, 300, 500, 700)


    def startMusic(self):
        # print(str(self.music_path_list[self.row]))
        self.music.load(str(self.music_path_list[self.row]))
        self.music.play(1)
        
        self.isPause()
        
        if self.loop:
            self.restartMusic()
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


    def closeEvent(self, event):
        self.music.stop()
        sys.exit()
    

    def clickedExit(self):
        self.music.stop()
        sys.exit()


    def restartMusic(self):
        self.music.rewind()
    

    def pauseMusic(self):
        if self.pause:
            self.pauseButton.setText("Pause?")
            self.music.unpause()
            self.pause = False
        else:
            self.pauseButton.setText("now Pausing")
            self.music.pause()
            self.pause = True


    def loopMusic(self):
        if self.loop:
            self.loopButton.setText("Loop?")
            self.loop = False
        else:
            self.loopButton.setText("now Looping")
            self.loop = True


    def nextMusic(self):
        if self.loop:
            self.restartMusic()
            return

        self.isPause()
        self.checkNext()
        self.startMusic()

    
    def checkNext(self):
        if self.row + 1 < len(self.music_list):
            self.row += 1
        else:
            self.row = 0
    

    # DnD! DnD! DnD!
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()


    # DnD! DnD! DnD!
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            x = Path(path)
            tmp = path.split('.')
            if x.name in self.FileList:
                continue
            if len(tmp) != 1:
                if x.suffix in ("mp3"):
                    self.music_list.addItem(x.name)
                    self.music_path_list.append(x)
            else:
                self.addDir(Path(tmp[0]))


    # DnD! DnD! DnD!
    def addDir(self, item):
        for s in item.glob("**/*.mp3"):
            self.music_list.addItem(s.name)
            self.music_path_list.append(s)
import os
import sys
import glob
import pygame
from PyQt5.QtWidgets import (
  QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget,
  QHBoxLayout
)
from PyQt5.QtCore import Qt

class Main(QMainWindow):
  def __init__(self):
    super(Main, self).__init__()
    self.MP = MusicPlayer()
    self.setCentralWidget(self.MP)
    self.initUI()
  
  def initUI(self):
    self.setGeometry(300, 300, 500, 200)
    self.setWindowTitle("Music Player")
    self.show()

class MusicPlayer(QWidget):
  def __init__(self, parent = None):
    super(MusicPlayer, self).__init__(parent)
    pygame.init()
    self.index = 0
    self.music = pygame.mixer.music
    self.root = os.path.abspath('./Music/')
    self.ext = 'mp3'
    self.pause = True
    self.loop = False
    self.initUI()

  def initUI(self):
    self.FileList = QListWidget(self)
    self.setFileList()
    self.FileList.itemSelectionChanged.connect(self.FileListChanged)
    self.fileName = self.FileList.item(self.index).text()

    startButton = QPushButton("Start")
    startButton.clicked.connect(self.startMusic)

    self.pauseButton = QPushButton("Pause?")
    self.pauseButton.clicked.connect(self.pauseMusic)

    nextButton = QPushButton("Next")
    nextButton.clicked.connect(self.nextMusic)

    buttonTopLayout = QHBoxLayout()
    buttonTopLayout.addWidget(startButton)
    buttonTopLayout.addWidget(self.pauseButton)
    buttonTopLayout.addWidget(nextButton)

    resetButton = QPushButton("Reset")
    resetButton.clicked.connect(self.resetMusic)

    self.loopButton = QPushButton("Loop?")
    self.loopButton.clicked.connect(self.loopMusic)

    exitButton = QPushButton("Exit")
    exitButton.clicked.connect(exit)

    buttonMidLayout = QHBoxLayout()
    buttonMidLayout.addWidget(self.loopButton)
    buttonMidLayout.addWidget(resetButton)
    buttonMidLayout.addWidget(exitButton)

    buttonVLayout = QVBoxLayout()
    buttonVLayout.addLayout(buttonTopLayout)
    buttonVLayout.addLayout(buttonMidLayout)

    allLayout = QHBoxLayout()
    allLayout.addWidget(self.FileList)
    allLayout.addLayout(buttonVLayout)

    self.setLayout(allLayout)

  def loopMusic(self):
    if self.loop:
      self.loopButton.setText("Loop?")
      self.loop = False
    else:
      self.loopButton.setText("Clicked Loop?")  
      self.loop = True

  def startMusic(self):
    self.music.load(self.root+self.fileName)
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
    files = glob.glob(self.root+"*."+self.ext)
    self.Files = sorted(files)
    for f in self.Files:
      self.FileList.addItem(os.path.basename(f))

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

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      exit
  
if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = Main()
  exit(app.exec_())

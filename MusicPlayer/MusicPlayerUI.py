from PyQt5.QtWidgets import (
  QWidget, QGridLayout, QPushButton, QHBoxLayout
)

from pathlib import Path

class MusicPlayerUI(QWidget):
    def initUI(self):
        startButton = QPushButton("Start")
        startButton.clicked.connect(self.startMusic)

        self.pauseButton = QPushButton("Pause")
        self.pauseButton.clicked.connect(self.pauseMusic)

        nextButton = QPushButton("Next")
        nextButton.clicked.connect(self.nextMusic)

        self.loopButton = QPushButton("Loop?")
        self.loopButton.clicked.connect(self.loopMusic)
        
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.resetMusic)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.clickedExit)

        buttonlayout = QGridLayout()
        buttonlayout.addWidget(startButton, 0, 0)
        buttonlayout.addWidget(self.pauseButton, 0, 1)
        buttonlayout.addWidget(nextButton, 0, 2)
        buttonlayout.addWidget(self.loopButton, 1, 0)
        buttonlayout.addWidget(resetButton, 1, 1)
        buttonlayout.addWidget(exitButton, 1, 2)

        layout = QHBoxLayout()
        layout.addWidget(self.FileList)
        layout.addLayout(buttonlayout)
        
        self.setLayout(layout)

        self.setGeometry(300, 300, 700, 500)
    
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
                if x.suffix in ("mp3", "m4a"):
                    self.FileList.addItem(x.name)
                    self.FilePathList.append(x)
            else:
                self.addDir(Path(tmp[0]))

    # DnD! DnD! DnD!
    def addDir(self, item):
        for item in [f for f in self.music_dir.glob("**/*") if re.search(r".+\.(mp3|m4a)", f.name)]:
            self.FileList.addItem(item.name)
            self.FilePathList.append(item)
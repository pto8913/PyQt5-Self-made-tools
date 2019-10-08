import sys
import img2pdf
from pathlib import Path
from PIL import Image 
from PyQt5.QtWidgets import (
  QApplication, QListWidget, QMessageBox,
)

from PyQt5.QtGui import QFont

from img_to_pdfUI import MainUI, LayoutUI

class Main(MainUI):
    def __init__(self):
        super(Main, self).__init__()

        self.myLayout = Layout()
        self.setCentralWidget(self.myLayout)
        self.initUI()
    

class Layout(LayoutUI):
    def __init__(self, parent = None):
        super(Layout, self).__init__(parent)
        
        self.setAcceptDrops(True)
        self.ImagePathList = []
        self.SelectFileName = ""
        self.Extension = ".jpg"
        self.FileList = QListWidget()

        self.PathInit()
        self.initUI()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            x = Path(path)
            tmp = path.split('.')
            if x in self.FileList:
                QMessageBox.information(self, 'Warning', 'This file already in.', QMessageBox.Ok)
                continue
            if len(tmp) != 1:
                if x.suffix == self.Extension:
                    self.FileList.addItem(x.name)
                    self.ImagePathList.append(x)
            else:
                print(tmp[0])
                self.__addDir(Path(tmp[0]))

    def __addDir(self, item: str) -> None:
        for f in list(item.glob("**/*.{}".format(self.Extension))):
            self.FileList.addItem(f.name)
            self.ImagePathList.append(f)

    def PathInit(self):
        self.current_dir = Path().resolve()

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = Main()
    w.setWindowTitle('img2pdf')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()
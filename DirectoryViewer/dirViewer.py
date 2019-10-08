import sys
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont

class DirViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.fileModel = QFileSystemModel()
        self.fileModel.setRootPath('')
        self.treeView = QTreeView()
        self.treeView.setModel(self.fileModel)

        self.treeView.setIndentation(10)    
        self.treeView.setSortingEnabled(True)

        self.treeView.setWindowTitle("Dir Viewer")
        self.treeView.resize(700, 300)

        vbox = QVBoxLayout()
        vbox.addWidget(self.treeView)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 700, 300)
        self.setWindowTitle("Dir Viewer")
        self.show()

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = DirViewer()
    w.setWindowTitle('DirViewer')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()

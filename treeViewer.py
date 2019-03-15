import sys
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout

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

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = DirViewer()
  sys.exit(app.exec_())

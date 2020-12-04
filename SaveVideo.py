from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QFont
import sys

from UI.SaveVideoUI import SaveVideoUI
from MainProcess.MainProcess import MainProcess

class Main(SaveVideoUI):
    def __init__(self):
        super(Main, self).__init__()

        self.main_process = MainProcess()
        self.setCentralWidget(self.main_process)

        self.InitUI()

def main():
    app = QApplication(sys.argv)
    font = QFont("Meiryo")
    app.setFont(font)
    w = Main()
    w.setWindowTitle("SaveVideo")
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()


import cv2

file_path = ""
delay = 1
window_name = 'frame'

cap = cv2.VideoCapture(file_path)

import sqlite3
from pathlib import Path
import numpy as np

p = Path().cwd()

conn = sqlite3.connect(f"{str(p)}/SaveVideo.db")
cur = conn.cursor()

cur.execute("select * from SaveVideo")
a = cur.fetchone()

print(a[0])
v = np.frombuffer(a[1])

videodata = np.loadtxt(a[1])
audiodata = np.loadtxt(a[2])

# need to change convert process and following function

import os
import re
import sys
import sqlite3
from PyQt5.QtWidgets import (
  QApplication, QListWidget, QMessageBox, QPushButton, QWidget, QCheckBox, QHBoxLayout,
  QGridLayout, QVBoxLayout, QLineEdit, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Main(QWidget):
  def __init__(self, parent = None):
    super(Main, self).__init__(parent)

    # use for convert
    self.elev_ptn = re.compile(r"(.*),(.*)")
    self.file_ptn = re.compile(r"FG-GML-(.*)-(.*)-(.*)-.*(A|B|C)-.*.xml")
    self.sp_ptn = re.compile(r"<gml:startPoint>(.*) (.*)</gml:startPoint>")
    self.lc_ptn = re.compile(r"<gml:lowerCorner>.* (.*)</gml:lowerCorner>")
    self.uc_ptn = re.compile(r"<gml:upperCorner>(.*) .*</gml:upperCorner>")
    self.load_cnt = 0
    self.cnt = 0
    self.sp = 0

    # lat
    self.lc_lat = 0
    self.lat_index = 0
    self.lat_diff = 0.008333333

    # lon
    self.lc_lon = 0
    self.lon_index = 0

    # Later: I will support 10m DEM and more
    self.width = 225
    self.height = 150
    self.size = self.width * self.height

    self.root_dir, self.db_dir, self.xml_dir = "", "", ""
    self.getDir()

    # Is list reverse?
    self.isReverse = False

    # DnD 
    self.setAcceptDrops(True)
    
    # path list
    self.xmlPathList = []
    self.FileList = QListWidget()
        
    self.initUI()

  def initUI(self):
    sortCheckBox = QCheckBox("reverse sort")
    sortCheckBox.stateChanged.connect(self.checkReverse)

    startButton = QPushButton("Start")
    startButton.clicked.connect(self.clickedStart)

    exitButton = QPushButton("Exit")
    exitButton.clicked.connect(self.clickedExit)

    sortButton = QPushButton("Sort Item")
    sortButton.clicked.connect(self.clickedSort)

    addButton = QPushButton("Add Item")
    addButton.clicked.connect(self.clickedAdd)

    deleteButton = QPushButton("Delete Item")
    deleteButton.clicked.connect(self.clickedDelete)

    clearButton = QPushButton("Clear Item")
    clearButton.clicked.connect(self.clickedClear)

    buttonLayout = QGridLayout()
    buttonLayout.addWidget(startButton, 0, 0)
    buttonLayout.addWidget(addButton, 0, 1)
    buttonLayout.addWidget(sortButton, 0, 2)
    buttonLayout.addWidget(deleteButton, 1, 0)
    buttonLayout.addWidget(clearButton, 1, 1)
    buttonLayout.addWidget(exitButton, 1, 2)
    buttonLayout.addWidget(sortCheckBox, 2, 1, 1, 1)

    layout = QHBoxLayout()
    layout.addLayout(buttonLayout)
    layout.addWidget(self.FileList)

    self.setLayout(layout)
    self.setGeometry(300, 300, 1000, 500)

  def clickedStart(self):
    table_tmp = 0
    check_file_tmp = 0
    for (index, xml_path) in enumerate(self.xmlPathList):
      match_file = self.file_ptn.search(os.path.basename(xml_path))

      # When the same file of DEM5A and DEM5B exists in the list
      check_for_DEM_x = match_file.group(1) + '-' + match_file.group(2) + '-' + match_file.group(3)
      if index + 1 != len(self.xmlPathList) and check_for_DEM_x in self.xmlPathList[index + 1]:
        print(1)
        if self.checkNextFileDEMType(self.xmlPathList[index + 1]):
          print(2)
          continue

      table = match_file.group(1) + match_file.group(2)
      if table != table_tmp:
        table_tmp = table
        self.convertReset()
        check_file_tmp = 0

      self.check_file = int(match_file.group(3))
      check_file_diff = self.check_file - check_file_tmp
      self.checkMissingFile(check_file_diff)
      check_file_tmp = self.check_file
      
      conn = sqlite3.connect(self.db_dir + "terrain.db")
      cur = conn.cursor()
      sql = cur.execute
      self.table_name = "fg" + table
      sql("""
        CREATE TABLE IF NOT EXISTS {} 
        (elevation double(5, 2), 
        lat_index int,
        lon_index int,
        lc_lat_num int, 
        lc_lon_num int, 
        uc_lat_num int, 
        uc_lon_num int);""".format(self.table_name))

      self.getStartPoint(xml_path)
      elevation, lats, lons = self.convert(xml_path)

      query = """INSERT INTO {} 
              (elevation, lat_index, lon_index, lc_lat_num, lc_lon_num, uc_lat_num, uc_lon_num) 
              VALUES (?, ?, ?, ?, ?, ?, ?);""".format(self.table_name)
      dataset = [x for x in zip(elevation, lats, lons, self.lc_lats, self.lc_lons, self.uc_lats, self.uc_lons)]
      cur.executemany(query, dataset)
      conn.commit()
  
    cur.close()
    conn.close()
    QMessageBox.information(self, "Message", "Finished convert", QMessageBox.Ok)

  def MinLatLonIntoDB(self):
    conn = sqlite3.connect(self.db_dir + "latlon.db")
    cur = conn.cursor()
    sql = cur.execute
    if self.inTable(conn, cur):
      cur.close()
      conn.close()
      return 
    sql("CREATE TABLE IF NOT EXISTS {}(lat double(3, 9), lon double(3, 9))".format(self.table_name))
    sql("INSERT INTO {} (lat, lon) VALUES('{}', '{}')".format(self.table_name, self.lc_lat, self.lc_lon))
    conn.commit()
    cur.close()
    conn.close()

  def inTable(self, conn, cur):
    cur.execute("select * from sqlite_master where type = 'table';")
    while True:
      v = cur.fetchone()
      if v == None:
        break
      if self.table_name in v:
        return True
    return False

  def checkNextFileDEMType(self, next_file):
    match_file = self.file_ptn.search(os.path.basename(next_file))
    DEM_type = match_file.group(4)
    if DEM_type in ('B', 'C'):
      return True
    return False

  def convert(self, filename):
    with open(filename, "r", encoding="utf-8_sig") as f:
      
      elevations = []
      for line in f.readlines():
        lc_match = self.lc_ptn.search(line)
        if lc_match and self.load_cnt == 0 and self.cnt == 0:
          if not self.lc_lon:
            self.lc_lon = float(lc_match.group(1))
          lc_match = 0

        uc_match = self.uc_ptn.search(line)
        if uc_match and self.load_cnt == 0 and self.cnt == 0:
          if not self.lc_lat:
            uc_lat = float(uc_match.group(1))
            self.lc_lat = uc_lat - self.lat_diff
            self.MinLatLonIntoDB()
          uc_match = 0
          self.convertLoad()
          
            
        el_match = self.elev_ptn.search(line)
        if el_match:
          typ, data = line.split(",")
          data = float(data)
          if typ in (u"データなし", u"海水面", u"内水面"):
            data = -1000.0
          elevations.append(data)
      
      self.getLcUcNumArray()
      new_elevations = self.adjustArray(elevations)
      lats = [self.lat_index] * self.size
      lons = [self.lon_index] * self.size
      print(self.check_file, self.lat_index, self.lon_index, self.load_cnt)
      self.lon_index += 1
      return (new_elevations, lats, lons)
  
  def getLcUcNumArray(self):
    self.lc_lats, self.lc_lons, self.uc_lats, self.uc_lons = [], [], [], []
    lat_num = self.height + self.height * self.cnt
    lon_num = (self.load_cnt - 1) * self.width
    cnt = 0
    while cnt != self.size:
      if lon_num > self.load_cnt * self.width - 1:
        lon_num = (self.load_cnt - 1) * self.width
        lat_num -= 1
      self.lc_lats.append(lat_num - 1)
      self.lc_lons.append(lon_num)
      self.uc_lats.append(lat_num)
      self.uc_lons.append(lon_num + 1)
      lon_num += 1
      cnt += 1

  def adjustArray(self, array):
    res = [-1000.0] * self.sp + array + (self.size - self.sp - len(array)) * [-1000.0]
    return res

  def convertLoad(self):
    if self.load_cnt >= 10:
      self.cnt += 1
      self.lat_index += 1
      self.load_cnt = 0
      self.lon_index = 0
    self.load_cnt += 1
  
  def checkMissingFile(self, check_file_diff):
    # horizontal
    h_diff_length = check_file_diff % 10
    # vertical
    v_diff_length = check_file_diff // 10
    if v_diff_length == 0 and h_diff_length < 2:
      return
    if v_diff_length > 0 and h_diff_length == 0:
      print(1)
      self.load_cnt += v_diff_length * 10 + h_diff_length - 1
      self.cnt += self.load_cnt // 10
      self.lat_index = self.cnt
      self.load_cnt %= 10
      self.lon_index = self.load_cnt
      return
    if h_diff_length > 1:
      if self.load_cnt == 10:
        print(2)
        self.cnt += 1
        self.lat_index += 1
        self.load_cnt = 0
        self.lon_index = 0
      elif self.load_cnt > 10:
        print(3)
        self.cnt += self.load_cnt // 10
        self.lat_index = self.cnt
        self.load_cnt %= 10
        self.lon_index = self.load_cnt
    return

  def convertReset(self):
    self.load_cnt = 0
    self.cnt = 0
    self.lat_index = 0
    self.lon_index = 0

  def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()

  def dropEvent(self, event):
    urls = event.mimeData().urls()
    for url in urls:
      path = url.toLocalFile()
      self.FileList.addItem(os.path.basename(path))
      self.xmlPathList.append(path)

  def clickedClear(self):
    self.FileList.clear()
    self.xmlPathList = []

  def clickedExit(self):
    self.close()

  def clickedAdd(self):
    filename, ok = QFileDialog.getOpenFileNames(self, "Open File", self.xml_dir, filter = "xml file (*.xml)")
    # if clicked cancel
    if not ok:
      return 
    self.FileList.addItems(os.path.basename(filename))
    self.xmlPathList.append(filename)

  def checkReverse(self):
    if not self.isReverse:
      self.isReverse = True
    else:
      self.isReverse = False

  def clickedSort(self):
    if self.isReverse:
      self.xmlPathList.sort(key = lambda x: os.path.basename(x), reverse = True)
      self.FileList.sortItems(Qt.DescendingOrder)
    else:
      self.xmlPathList.sort(key = lambda x: os.path.basename(x))
      self.FileList.sortItems()

  def clickedDelete(self):
    try:
      row = self.FileList.row(self.FileList.selectedItems()[0])
      self.xmlPathList.pop(row)
      self.FileList.takeItem(row)
    except:
      pass

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.clickedExit()

  def getStartPoint(self, filename):
    with open(filename, "r", encoding="utf-8_sig") as f:
      while True:
        line = f.readline()
        sp_match = self.sp_ptn.search(line)
        if sp_match:
          sp_lon, sp_lat = int(sp_match.group(1)), int(sp_match.group(2))
          self.sp = sp_lat * self.width + sp_lon
          return

  def checkDir(self, dirname):
    if not os.path.exists(dirname):
      os.mkdir(dirname)

  def getDir(self):
    this_file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(this_file_dir + "/../../")
    self.root_dir = os.getcwd()

    self.db_dir = self.root_dir + "/DB/"
    self.checkDir(self.db_dir)
    self.xml_dir = self.root_dir + "/Terrain_xml_data/"
    self.checkDir(self.xml_dir)

def main():
  app = QApplication(sys.argv)
  font = QFont("Meiryo")
  app.setFont(font)
  w = Main()
  w.setWindowTitle("xml to db")
  w.show()
  w.raise_()
  app.exec_()

if __name__ == '__main__':
  main()

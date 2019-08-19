import os
import re
import sys
import sqlite3
from collections import deque
from PyQt5.QtWidgets import (
  QApplication, QListWidget, QLabel, 
  QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont

from xmlToDBUI import MainUI, MainProcessUI
from myfunc import function
from xmlToDBDirSetting import DirSetting as Ds

adjustSep = lambda x : Ds().adjustSep(x)
inExtension = lambda x : function().inExtension(x)

basename = lambda x: os.path.basename(x)

Search = lambda ptn, item: ptn.search(item)
Group = lambda match, index: match.group(index)

SEALEVEL = 32768

# 変数の前の__はプライベート変数(擬似)にするため、無理やりやればアクセスできるけど。
# The first __ of a variable is a private variable (suspected). You can force access...

class Notifier(QObject):
  notify = pyqtSignal()

class Thread(QThread):
  def __init__(self, notifier, name):
    super().__init__()
    self.notifier = notifier
    self.name = name

  def run(self):
    print('start thread :' + self.name)

    self.notifier.notify.emit()
    self.finished.emit()

class Main(MainUI):
  def __init__(self):
    super(Main, self).__init__()
    
    self.main_process = MainProcess()

    self.setCentralWidget(self.main_process)

    self.initUI()
    
class MainProcess(MainProcessUI):
  def __init__(self):
    super(MainProcess, self).__init__()

    # use for convert
    self.__elev_ptn = re.compile(r"(.*),(.*)")
    self.__file_ptn = re.compile(r"FG-GML-(.*)-(.*)-(.*)-.*(A|B|C)-.*.xml")
    self.__sp_ptn = re.compile(r"<gml:startPoint>(.*) (.*)</gml:startPoint>")
    self.__lc_ptn = re.compile(r"<gml:lowerCorner>.* (.*)</gml:lowerCorner>")
    self.__uc_ptn = re.compile(r"<gml:upperCorner>(.*) .*</gml:upperCorner>")
    self.__load_cnt = 0
    self.__cnt = 0
    self.__sp = 0

    self.__missing = False

    self.__lat_for_file0 = set()
    self.__lon_for_file0 = set()

    # lat
    self.__lat_index = 0
    self.__lat_diff = 0.008333333

    # lon
    self.__lon_index = 0

    # Later: I will support 10m DEM and more
    self.__width = 225
    self.__height = 150
    self.__size = self.__width * self.__height

    self.__db_dir, self.__xml_dir = Ds().getDir()

    #self.lc_lats, self.lc_lons, self.uc_lats, self.uc_lons = [], [], [], []
    #self.__getLcNumArray()

    self.__que = deque()

    # DnD 
    self.setAcceptDrops(True)
    
    # path list
    self.__xmlPathList = []
    self.FileList = QListWidget()

    self.initUI()
  
  def onClicked(self):
    if len(self.__xmlPathList) == 0:
      return
    # start sub_process
    self.notifier = Notifier()
    self.thread = Thread(self.notifier, "convert")
    self.notifier.moveToThread(self.thread)
    self.notifier.notify.connect(self.__clickedStart, type = Qt.DirectConnection)
    self.thread.start()
    self.thread.finished.connect(self.__finishSubProcess)

  def __clickedStart(self):
    table_tmp = 0
    cnt = 0
    check_file_tmp = -1
    xmlPathList = self.__xmlPathList[:]
    for index, xml_path in enumerate(xmlPathList):
      match_file = Search(self.__file_ptn, basename(xml_path))

      # When the same file of DEM5A and DEM5B exists in the list
      check_for_DEM_x = Group(match_file, 1) + '-' + Group(match_file, 2) + '-' + Group(match_file, 3)
      if index + 1 != len(xmlPathList) and check_for_DEM_x in xmlPathList[index + 1]:
        if self.__checkNextFileDEMType(xmlPathList[index + 1]):
          continue

      table = Group(match_file, 1) + Group(match_file, 2)
      if table != table_tmp:
        if self.__lat_for_file0 and self.__lon_for_file0:
          self.__MinLatLonIntoDB(min(self.__lat_for_file0), min(self.__lon_for_file0))
        table_tmp = table
        self.__convertReset()
        check_file_tmp = -1
        cnt = 0

      check_file = int(Group(match_file, 3))
      check_file_diff = check_file - check_file_tmp
      if check_file_diff > 1:
        self.__missing = True
      check_file_tmp = check_file

      conn = sqlite3.connect(self.__db_dir + "testterrain6.db")
      cur = conn.cursor()
      sql = cur.execute
      self.__table_name = "fg" + table
      sql("""
        CREATE TABLE IF NOT EXISTS {} 
        (elevation double(5, 2), 
         lat_index int,
         lon_index int,
        lc_lat_num int, 
        lc_lon_num int, 
        uc_lat_num int, 
        uc_lon_num int);""".format(self.__table_name))

      query = """INSERT INTO {} 
              (elevation, lat_index, lon_index, lc_lat_num, lc_lon_num, uc_lat_num, uc_lon_num) 
              VALUES (?, ?, ?, ?, ?, ?, ?);""".format(self.__table_name)
      cnt += check_file_diff
      if self.__missing:
        for _ in range(check_file_diff - 1):
          elevation, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons = self.__GetMissing()
          dataset = [x for x in zip(elevation, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons)]
          cur.executemany(query, dataset)
          conn.commit()
        self.__missing = False
      self.__getStartPoint(xml_path)
      elevation, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons = self.__convert(xml_path)

      dataset = [x for x in zip(elevation, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons)]
      cur.executemany(query, dataset)
      conn.commit()

      if xml_path == xmlPathList[-1]:
        self.__MinLatLonIntoDB(min(self.__lat_for_file0), min(self.__lon_for_file0))

        match = Search(self.__file_ptn, xml_path)
        file_name = int(Group(match, 3))
        if file_name != 99:
          for _ in range(99 - file_name):
            elevation, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons = self.__GetMissing()
            dataset = [x for x in zip(elevation, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons)]
            cur.executemany(query, dataset)
            conn.commit()
    cur.close()
    conn.close()
    print(cnt)

  def __finishSubProcess(self):
    #QMessageBox.information(self, "Message", "Finished convert", QMessageBox.Ok)
    print("fin")

  def __checkNextFileDEMType(self, next_file):
    match_file = self.__file_ptn.search(os.path.basename(next_file))
    DEM_type = match_file.group(4)
    if DEM_type in ('A', 'B', 'C'):
      return True
    return False

  def __GetMissing(self):
    elev = [SEALEVEL - 1000] * self.__size
    self.__convertLoad()
    lc_lats, lc_lons, uc_lats, uc_lons = self.__getLcUcNumArray()
    lats = [self.__lat_index] * self.__size
    lons = [self.__lon_index] * self.__size
    self.__lon_index += 1
    return (elev, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons)

  def __convertReset(self):
    self.__load_cnt = 0
    self.__cnt = 0
    self.__lat_index = 0
    self.__lon_index = 0
    self.__lat_for_file0 = set()
    self.__lon_for_file0 = set()

  def __convert(self, filename):
    with open(filename, "r", encoding="utf-8_sig") as f:
      elevations = []
      for line in f.readlines():
        lc_match = self.__lc_ptn.search(line)
        if lc_match:
          lc_lon = float(lc_match.group(1))
          self.__lon_for_file0.add(lc_lon)
          lc_match = 0

        uc_match = self.__uc_ptn.search(line)
        if uc_match:
          uc_lat = float(uc_match.group(1))
          lc_lat = uc_lat - self.__lat_diff
          self.__lat_for_file0.add(lc_lat)
          self.__MinLatLonIntoDB(lc_lat, lc_lon)
          uc_match = 0
          self.__convertLoad()
            
        el_match = self.__elev_ptn.search(line)
        if el_match:
          typ, data = line.split(",")
          data = float(data)
          if typ in (u"データなし", u"海水面", u"内水面"):
            data = -1000.0
          elevations.append(data)
    
    lc_lats, lc_lons, uc_lats, uc_lons = self.__getLcUcNumArray()
    new_elevations = self.__adjustArray(elevations)
    lats = [self.__lat_index] * self.__size
    lons = [self.__lon_index] * self.__size
    #print(self.lat_index, self.lon_index, self.load_cnt)
    self.__lon_index += 1
    f.close()
    return (new_elevations, lats, lons, lc_lats, lc_lons, uc_lats, uc_lons)

  def __convertLoad(self):
    if self.__load_cnt >= 10:
      self.__cnt += 1
      self.__lat_index += 1
      self.__load_cnt = 0
      self.__lon_index = 0
    self.__load_cnt += 1
  
  def __getLcUcNumArray(self):
    lc_lats, lc_lons, uc_lats, uc_lons = [], [], [], []
    lat_num = self.__height + self.__height * self.__cnt
    lon_num = (self.__load_cnt - 1) * self.__width
    #print(lat_num, lon_num)
    cnt = 0
    while cnt != self.__size:
      if lon_num > self.__load_cnt * self.__width - 1:
        lon_num = (self.__load_cnt - 1) * self.__width
        lat_num -= 1
      lc_lats.append(lat_num - 1)
      lc_lons.append(lon_num)
      uc_lats.append(lat_num)
      uc_lons.append(lon_num + 1)
      lon_num += 1
      cnt += 1
    return (lc_lats, lc_lons, uc_lats, uc_lons)

  def __getStartPoint(self, filename):
    with open(filename, "r", encoding="utf-8_sig") as f:
      while True:
        line = f.readline()
        sp_match = self.__sp_ptn.search(line)
        if sp_match:
          sp_lon, sp_lat = int(sp_match.group(1)), int(sp_match.group(2))
          self.__sp = sp_lat * self.__width + sp_lon
          return

  def __adjustArray(self, array):
    return [-1000.0] * self.__sp + array + (self.__size - self.__sp - len(array)) * [-1000.0]

  def __MinLatLonIntoDB(self, lc_lat, lc_lon):
    conn = sqlite3.connect(self.__db_dir + "latlon.db")
    cur = conn.cursor()
    sql = cur.execute
    if self.__inTable(conn, cur):
      cur.close()
      conn.close()
      return 
    sql("CREATE TABLE IF NOT EXISTS {}(lat double(3, 9), lon double(3, 9))".format(self.__table_name))
    sql("INSERT INTO {} (lat, lon) VALUES('{}', '{}')".format(self.__table_name, lc_lat, lc_lon))
    conn.commit()
    cur.close()
    conn.close()

  def __inTable(self, conn, cur):
    cur.execute("select * from sqlite_master where type = 'table';")
    while True:
      v = cur.fetchone()
      if v == None:
        break
      if self.__table_name in v:
        return True
    return False

  def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
      event.accept()
    else:
      event.ignore()

  def dropEvent(self, event):
    urls = event.mimeData().urls()
    for url in urls:
      path = adjustSep(url.toLocalFile())
      tmp = path.split('.')
      if path in self.__xmlPathList:
        QMessageBox.information(self, 'Warning', 'This file already in.', QMessageBox.Ok)
        continue
      if len(tmp) != 1:
        if inExtension(path):
          self.FileList.addItem(basename(path))
          self.__xmlPathList.append(path)
      else:
        self.__addDir(tmp[0])
  
  def __addDir(self, item):
    for roots, dirs, files in os.walk(item):
      for f in files:
        if inExtension(f):
          self.FileList.addItem(basename(f))
          self.__xmlPathList.append(adjustSep(roots + '/' + f))

      if len(dirs) != 0:
        for d in dirs:
          self.__que.append(d)
        return self.__addDir(self.__que.popleft())

    try:
      if len(self.__que) != 0:
        return self.__addDir(self.__que.popleft())
    except:
      return

  def clickedClear(self):
    self.FileList.clear()
    self.__xmlPathList = []

  def clickedExit(self):
    exit()

  def clickedAdd(self):
    filename, ok = QFileDialog.getOpenFileNames(self, "Open File", self.__xml_dir, filter = "xml file (*.xml)")
    # if clicked cancel
    if not ok:
      return 
    for f in filename:
      f = adjustSep(f)
      if f in self.__xmlPathList:
        continue
      self.FileList.addItem(basename(f))
      self.__xmlPathList.append(self.replaceSep(f))

  def clickedSort(self):
    self.__xmlPathList.sort(key = lambda x: basename(x))
    self.FileList.sortItems()

  def clickedDelete(self):
    try:
      row = self.FileList.row(self.FileList.selectedItems()[0])
      self.__xmlPathList.pop(row)
      self.FileList.takeItem(row)
    except:
      pass

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
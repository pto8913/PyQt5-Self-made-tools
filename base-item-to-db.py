import os
import sys
import re

from collections import deque
import numpy as np
import matplotlib.pyplot as plt

building_ptn = re.compile(r"FG-GML-.*-Bld(A|L)-.*-.*")
position_ptn = re.compile(r"<gml:posList>")
fin_pos_ptn = re.compile(r"</gml:posList>")
data_ptn = re.compile(r"(.*) (.*)")

class Detail():
  def __inExtension(self, item, extension):
    if item.split(".")[1] == extension:
      return True
    return False

  def __changeSep(self, item):
    return item.replace('/', os.sep)

  def __checkDir(self, dirname):
    if not os.path.exists(dirname):
      os.mkdir(dirname)

  def __getDir(self):
    self.__this_file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(self.__this_file_dir + '/../../')
    self.__root_dir = os.getcwd()

    self.__db_dir = self.__root_dir + '/DB/'
    self.__checkDir(self.__db_dir)
    
    self.__xml_dir = self.__root_dir + '/Terrain_xml_data/'
    self.__checkDir(self.__xml_dir)
    
    self.__save_fig_dir = self.__root_dir + '/Image/'
    self.__checkDir(self.__save_fig_dir)

    os.chdir(self.__this_file_dir + '/../')
    self.__base_xml_dir = os.getcwd() + '/Base_item/'
    self.__checkDir(self.__base_xml_dir)
    
    os.chdir(self.__this_file_dir + '/terrain_module/')
    self.__module_dir = os.getcwd()
    self.__checkDir(self.__module_dir)
    return (self.__db_dir, self.__xml_dir, self.__save_fig_dir, self.__base_xml_dir, self.__module_dir)

  def __addPath(self):
    for dir_path in self.__getDir():
      sys.path.append(self.__changeSep(dir_path))
    import mylatlon

    self.mylatlon = mylatlon

class Main():
  def __init__(self):
    super(Main, self).__init__()

    self.detail = Detail()
    self.detail._Detail__addPath()

  def convert(self, filepath):
    with open(filepath, encoding = 'utf-8_sig') as f:
      result = []
      tmp = []
      data = False
      for line in f.readlines():
        match_pos = position_ptn.search(line)
        if match_pos:
          line = f.readline()
          data = True
          match_pos = 0
        
        match_data = data_ptn.search(line)
        if match_data and data:
          lat, lon = map(float, line.split())
          tmp.append((lat, lon))
        
        match_fin_pos = fin_pos_ptn.search(line)
        if match_fin_pos:
          result.append(tmp)
          tmp = []
          match_fin_pos = 0
          data = False
          match_data = 0
      f.close()
      return result

  def start(self):
    for roots, dirs, files in os.walk(self.detail._Detail__base_xml_dir):
      for f in files:
        if self.detail._Detail__inExtension(f, "xml"):
          match_file = building_ptn.search(f)
          if match_file:
            res = self.convert(self.detail._Detail__changeSep(roots + '/' + f))
            print(res)

      if len(dirs) != 0:
        self.__que = deque()
        for d in dirs:
          self.__que.append(d)
        self.__addDir
  
  def __addDir(self):
    for roots, dirs, files in os.walk(self.__que.popleft()):
      for f in files:
        if self.detail._Detail__inExtension(f, "xml"):
          match_file = building_ptn.search(f)
          if match_file:
            res = self.convert(self.detail._Detail__changeSep(roots + '/' + f))
            print(res)
  
      if len(dirs) != 0:
        for d in dirs:
          self.__que.append(d)
        return self.__addDir()
  
    if len(self.__que) != 0:
      return self.__addDir()


if __name__ == "__main__":
  x = Main()
  x.start()
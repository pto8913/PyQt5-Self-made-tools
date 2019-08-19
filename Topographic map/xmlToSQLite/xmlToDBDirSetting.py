import os
import sys

class DirSetting:
  def __checkDir(self, dirname):
    if not os.path.exists(dirname):
      os.mkdir(dirname)
      
  def getDir(self):
    __this_file_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
    os.chdir(__this_file_dir + "/../")
    __root_dir = os.getcwd()

    __db_dir = self.adjustSep(__root_dir + "/DB/")
    self.__checkDir(__db_dir)
    __xml_dir = self.adjustSep(__root_dir + "/Terrain_xml_data/")
    self.__checkDir(__xml_dir)
    self.__addDirPath((__this_file_dir, __db_dir, __xml_dir))
    return __db_dir, __xml_dir

  def __addDirPath(self, paths):
    for path in paths:
      sys.path.append(path)

  def adjustSep(self, path):
    return path.replace('/', os.sep)
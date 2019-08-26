import os
import sys

from .myfunc import adjustSep

class DirSetting:
  def __checkDir(self, dirname):
    if not os.path.exists(dirname):
      os.mkdir(dirname)
      
  def getDir(self):
    this_file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    os.chdir(this_file_dir + '/../')
    root_dir = adjustSep(os.getcwd())
  
    db_dir = adjustSep(root_dir + '/DB/')
    self.__checkDir(db_dir)
    return db_dir
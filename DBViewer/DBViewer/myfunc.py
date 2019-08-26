import os

def basename(item):
  return os.path.basename(item)

def inExtension(item, ext):
  try:
    if item.split(".")[-1] == ext:
      return True
  except:
    pass
  return False

def adjustSep(path):
  return path.replace('/', os.sep)
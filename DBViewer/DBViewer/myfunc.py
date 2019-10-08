class function:
  def inExtension(self, item: str, ext: str) -> bool:
    try:
      if ext in item.suffix:
        return True
    except:
      if ext in item:
        return True
    return False
  
  def basename(self, item: str) -> str:
    return str(item.name)
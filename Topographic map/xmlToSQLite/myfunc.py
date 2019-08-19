class function:
  def inExtension(self, item):
    try:
      if item.split(".")[-1] == "xml":
        return True
    except:
      pass
    return False

  def checkQuery(self, item):
    funcType = item.split(" ")[0].lower()

    if funcType == ("select"):
      return 0
    if funcType in ("insert", "update", "delete", "create", "drop", "alter"):
      return 1
    return -1

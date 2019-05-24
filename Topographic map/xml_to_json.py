import re
import os
import sys
import json

file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

addList = lambda x, arg: arg.append(x)
basename = lambda x: os.path.basename(x)
mySearch = lambda x, ptn: ptn.search(x)
myGroup = lambda x, mc: mc.group(x)
comp = lambda x: re.compile(x)

ptn_elev = comp(r"(.*),(.*)")
ptn_sp = comp(r"<gml:startPoint>(.*) (.*)</gml:startPoint>")

def new_convert(filename):
  result = {}
  with open(filename, "r", encoding = "utf-8_sig") as f:
    elevation = []
    for line in f.readlines():
      match_elev = mySearch(line, ptn_elev)
      if match_elev:
        typ, data = line.split(",")
        #data = int((float(data)*2 + 1) // 2)
        data = float(data)
        if typ in (u"データなし", u"海水面"):
          data = 0
        addList(data, elevation)

      match_sp = mySearch(line, ptn_sp)
      if match_sp:
        result["sp"] = (int(myGroup(1, match_sp)), int(myGroup(0, match_sp)))
        break

  result["sp"] = result["sp"][1] * 225 + result["sp"][0]
  if not os.path.exists(dir_dest):
    os.mkdir(dir_dest)

  data = {"startPoint": meta["sp"], "elevations": elevation}
  json.dump(
    data,
    open(dir_dest + "{}.json".format(dest_filebase), "w")
  )

if __name__ == '__main__':
  for roots, dirs, files in os.walk(file_dir+"/"):
    for f in files:
      if f.split(".")[1] == "xml":
        filename = roots + "/" + f
        new_convert(filename)

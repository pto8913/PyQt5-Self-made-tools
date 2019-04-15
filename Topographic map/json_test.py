import re
import os
import sys
import json

odir = lambda x: os.path.dirname(x)
opath = lambda x: os.path.abspath(x)
oname = lambda x: os.path.basename(x)
oexis = lambda x: os.path.exists(x)
mkd = lambda x: os.mkdir(x)
comp = lambda x: re.compile(x)
mySearch = lambda x, ptn: ptn.search(x) 
myGroup = lambda x, ma: ma.group(x)
addList = lambda x, arg: arg.append(x)
wrt = lambda x, f: f.write(x)

fileDir = odir(opath(sys.argv[0]))

ptnElev = comp(r"(.*),(.*)")
ptnSp = comp(r"<gml:startPoint>(.*) (.*)</gml:startPoint>")
ptnFile = comp(r"FG-GML-(.*)-(.*)-(.*)-.*-.*.xml")
ptnLc = comp(r"<gml:lowerCorner>(.*) (.*)</gml:lowerCorner>")

x = False
count = 1
tmp = [[0, 0]]
saveTmp = ""
def convert(filename):
  global x, count, tmp, saveTmp
  searchFile = mySearch(filename, ptnFile)
  fileBaseName = myGroup(3, searchFile) # 01 , 02, 
  name = oname(filename)
  saveDirectory = opath(filename).replace(name,"") + "_json_n_txt/"
  if saveTmp != saveDirectory:
    x = False
    tmp = [[0, 0]]
    saveTmp = saveDirectory
    count = 1

  if not oexis(saveDirectory):
    mkd(saveDirectory)
    
  with open(filename, "r", encoding = "utf-8_sig") as f:
    elevation = []
    meta = {}
    for line in f.readlines():
      searchLc = mySearch(line, ptnLc)
      if searchLc:
        if not oexis(saveDirectory + "txt/"):
          mkd(saveDirectory + "txt/")
        with open(saveDirectory + "txt/"+ "{}.txt".format(fileBaseName), "w") as wf:
          if not x:
            lat, lon = (searchLc.group(1), searchLc.group(2))
            wrt(str(lat) + "," + str(lon), wf)
            for i in range(11):
              addList([lat, float(lon)+i*0.013], tmp)
          else:
            lat, lon = float(tmp[-1][0]), float(tmp[count][1])
            a = 0.0083333
            if count == 11:
              lat = round(lat+a, 9)
              wrt(str(lat)+","+str(tmp[1][1]), wf)
              addList((lat, lon), tmp)
              count = 1
            else:
              wrt(str(lat) + "," + str(lon), wf)
          x = True
          count += 1
          
          """
            lat, lon = float(tmp[-1][0]), float(tmp[count][1])
            a = 0.008333
            if count == 11:
              lat = round(lat + a, 9)
              wrt(str(lat)+","+str(tmp[1][1])+"\n", wf)
              addList((lat, lon), tmp)
              count = 1
            else:
              wrt(str(lat)+","+str(lon)+"\n", wf)
          else:
            lat, lon = myGroup(1, searchLc), myGroup(2, searchLc)
            wrt(str(lat)+","+str(lon)+"\n", wf)
            for i in range(11):
              addList([lat, float(lon)+i*0.013], tmp)
          x = True
          count += 1
          """
      #print(tmp)
      searchElev = mySearch(line, ptnElev)
      if searchElev:
        typ, data = line.split(",")
        if typ in (u"データなし", u"海水面"):
          data = u"Nan"
        addList(float(data), elevation)

      searchSp = mySearch(line, ptnSp)
      if searchSp:
        meta["sp"] = (int(myGroup(1, searchSp)), int(myGroup(1, searchSp)))
        break

  meta["shape"] = (225, 150)
  meta["sp"] = meta["sp"][1] * 225 + meta["sp"][0]

  data = {"startPoint": meta["sp"], "elevations": elevation}
  if not oexis(saveDirectory + "json/"):
    mkd(saveDirectory + "json/")
  json.dump(
    data,
    open(saveDirectory + "json/" + "{}.json".format(fileBaseName), "w")
  )

if __name__ == "__main__":
  for roots, dirs, files in os.walk(fileDir+"/"):
    for f in files:
      if f.split(".")[1] == "xml":
        fileName = roots + "/" + f
        convert(fileName)
        #print(fileName)
        #exit()
import re
import os
import sys
import json

ptn_elev = re.compile(r"(.*),(.*)")
ptn_sp = re.compile(r"<gml:startPoint>(.*) (.*)</gml:startPoint>")
ptn_file = re.compile(r"FG-GML-(.*)-(.*)-(.*)-.*-.*.xml")

root = os.path.dirname(os.path.abspath(sys.argv[0]))

def convert(filename):
  elevations = []
  meta = {}
  with open(filename, "r", encoding = "utf-8_sig") as f:
    while True:
      line = f.readline()
      match_elev = ptn_elev.search(line)
      if match_elev:
        typ, data = line.split(",")
        if typ in (u"データなし", u"海水面"):
          data = u"Nan"
        elevations.append(float(data)) 
      match_sp = ptn_sp.search(line)
      if match_sp:
        meta["sp"] = (int(match_sp.group(1)), int(match_sp.group(2)))
        break
  shape = (225, 150)
  meta["shape"] = shape
  meta["sp"] = meta["sp"][1] * 225 + meta["sp"][0]
  match_file = ptn_file.match(os.path.basename(filename))
  dir_dest = root + "/" + root[-20:]+"_json/"
  dest_filebase = "{}".format(match_file.group(3))
  data = {"startPoint": meta["sp"], "elevations": elevations}
  json.dump(
    data,
    open(dir_dest + "{}.json".format(dest_filebase), "w")
  )

for roots, _, files in os.walk(root + "/"):
  for f in files:
    file_name = os.path.join(roots, f)
    convert(file_name)
    print(file_name)

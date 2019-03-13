import re
import os
import json
from os import path

# 作る過程で等高線を表示するなどを試していたためlcやucが入っている
def convert(filename):
  ptn_lc = (re.compile(r"<gml:lowerCorner>(.*) (.*)</gml:lowerCorner>"), 'lc', float) # group(1) 最小の緯度 group(2) 最小の経度
  ptn_uc = (re.compile(r"<gml:upperCorner>(.*) (.*)</gml:upperCorner>"), 'uc', float) # group(1) 最大の緯度 group(2) 最大の経度
  ptn_low = (re.compile(r"<gml:low>(.*) (.*)</gml:low>"), 'low', int) # セルの最小値
  ptn_high = (re.compile(r"<gml:high>(.*) (.*)</gml:high>"), 'high', int) # セルの最大値
  ptn_sp = (re.compile(r"<gml:startPoint>(.*) (.*)</gml:startPoint>"), 'sp', int) # 値の開始位置
  ptn_elev = (re.compile(r"(.*),(.*)")) # 標高値とデータの種類
  ptn_file = re.compile(r'FG-GML-(.*)-(.*)-(.*)-.*-.*.xml') # xmlファイル
  meta = {}
  elevations = []
  with open(filename, encoding = 'utf-8') as f:
    while True:
      # ファイルの中身を一行ずつ読み込む
      line = f.readline()
      match_lc = ptn_lc[0].search(line)
      if(match_lc):
        # group(1) 最小の緯度 group(2) 最小の経度
        meta[ptn_lc[1]] = (ptn_lc[2](match_lc.group(1)), ptn_lc[2](match_lc.group(2)))
      match_uc = ptn_uc[0].search(line)
      if(match_uc):
        # group(1) 最大の緯度 group(2) 最大の経度
        meta[ptn_uc[1]] = (ptn_uc[2](match_uc.group(1)), ptn_uc[2](match_uc.group(2)))
      match_low = ptn_low[0].search(line)
      if(match_low):
        # セルの最小値
        meta[ptn_low[1]] = (ptn_low[2](match_low.group(1)), ptn_low[2](match_low.group(2)))
      match_high = ptn_high[0].search(line)
      if(match_high):
        # セルの最大値
        meta[ptn_high[1]] = (ptn_high[2](match_high.group(1)), ptn_high[2](match_high.group(2)))
      match_elev = ptn_elev.search(line)
      if(match_elev):
        # 標高値とその種類
        typ, data = line.strip().split(',')
        if(typ in (u'データなし', u'海水面')):
          data = u'NaN'
        elevations.append(float(data))
      match_sp = ptn_sp[0].search(line)
      if(match_sp):
        # 値の開始位置
        meta[ptn_sp[1]] = (ptn_sp[2](match_sp.group(1)), ptn_sp[2](match_sp.group(2)))
        break
  # print(meta)
  # shape: 配列の大きさ
  shape = (meta['high'][1] + 1, meta['high'][0] + 1)
  meta['shape'] = shape
  meta['sp'] = meta['sp'][1] * shape[1] + meta['sp'][0]
  # path.basenameでファイルの名前をとる
  match_file = ptn_file.match(path.basename(filename))
  # ファイルの保存先のパス group(1): 5233 group(2): 07
  dir_dest = "Path_where_data_is_stored/{}/{}".format(match_file.group(1), match_file.group(2))
  #group(3): __.xml
  dest_filebase = "{}".format(match_file.group(3))
  # startPointとelevationsというキーにそれぞれmeta['sp'], elevationsを要素に
  data = {"startPoint": meta['sp'], "elevations": elevations}
  json.dump(
    data,
    open(path.join(dir_dest, "{}.json".format(dest_filebase)), "w")
  )

# root: 現在のディレクトリ dirs: root下に存在するディレクトリ files: root下に存在するファイル
for root, dirs, files in os.walk("Path_with_data"):
  for fn in files:
    file_name = path.join(root, fn)
    convert(file_name)
    print(file_name)

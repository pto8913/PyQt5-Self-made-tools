import re
import os
import sys
import json

# 標高データを抜き出す正規表現
ptn_elev = re.compile(r"(.*),(.*)")
# データの開始地点を抜き出す正規表現
ptn_sp = re.compile(r"<gml:startPoint>(.*) (.*)</gml:startPoint>")
# ファイル名を抜き出す正規表現
ptn_file = re.compile(r"FG-GML-(.*)-(.*)-(.*)-.*-.*.xml")
# マップの左下の位置
ptn_lc = re.compile(r"<gml:lowerCorner>(.*) (.*)</gml:lowerCorner>")
# ファイルが保存してあるディレクトリ
root = os.path.dirname(os.path.abspath(sys.argv[0]))

def convert(filename):
  # 標高データを入れる配列
  elevations = []
  # データをjsonファイルにするために使う辞書型配列
  meta = {}
  # ファイルを開く utf-8_sigの部分は各々の環境によって変わるかもしれません
  with open(filename, "r", encoding = "utf-8_sig") as f:
    while True:
      # ファイルを一行ずつ読み込む
      line = f.readline()
      # ファイル名とマッチしているか
      match_file = ptn_file.match(os.path.basename(filename))
      # ファイル名
      dest_filebase = "{}".format(match_file.group(3))
      # lcとマッチするか
      match_lc = ptn_lc.search(line)
      if match_lc:
        # ファイルを書き込むためにtxtを開く
        dir_ = root + "/" + root[-20:]+"_txt/"
        # 保存先のディレクトリが存在しなかったらディレクトリを作成する
        if not os.path.exists(dir_):
          os.mkdir(dir_)
        # ファイルを書き込むためにtxtを開く
        with open(dir_ + "{}.txt".format(dest_filebase), "w") as wf:
          # 書き込む
          wf.write(str(match_lc.group(1)) + "," + str(match_lc.group(2)) + "\n")
      # 標高のパターンにマッチするか探す
      match_elev = ptn_elev.search(line)
      # マッチしたら処理
      if match_elev:
        # データのタイプとデータに分割
        typ, data = line.split(",")
        # データのタイプがデータなしや海水面ならNanに
        if typ in (u"データなし", u"海水面"):
          data = u"Nan"
        # 標高データをfloat型にして追加
        elevations.append(float(data)) 
      # 開始地点のパターンとマッチするか探す
      match_sp = ptn_sp.search(line)
      # マッチたら処理
      if match_sp:
        # 開始地点を保存しておく
        meta["sp"] = (int(match_sp.group(1)), int(match_sp.group(2)))
        break
  # 配列の大きさ
  shape = (225, 150)
  meta["shape"] = shape
  meta["sp"] = meta["sp"][1] * 225 + meta["sp"][0]
  # ファイルの保存先のディレクトリ
  dir_dest = root + "/" + root[-20:]+"_json/"
  # 保存先のディレクトリが存在しなかったらディレクトリを作成する
  if not os.path.exists(dir_dest):
    os.mkdir(dir_dest)
  # startPointとelevationsというキーにそれぞれmeta['sp'], elevationsを要素に
  data = {"startPoint": meta["sp"], "elevations": elevations}
  json.dump(
    data,
    open(dir_dest + "{}.json".format(dest_filebase), "w")
  )
# root: 現在のディレクトリ dirs: root下に存在するディレクトリ files: root下に存在するファイル
for roots, _, files in os.walk(root + "/"):
  for f in files:
    file_name = os.path.join(roots, f)
    convert(file_name)
    print(file_name)

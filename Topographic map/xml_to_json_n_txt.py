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
# 一つ目のファイルだけ処理を行うため
x = False
# 配列の要素にアクセスするのと経度をリセットするときに使う
count = 1
# float型を足していくとオーバーフローして演算の結果がおかしくなるのであらかじめ
# とり得る経度の値を保存しておく
tmp = [[0, 0]]
def convert(filename):
  global x, count, tmp
  # 標高データを入れる配列
  elevations = []
  # データをjsonファイルにするために使う辞書型配列
  meta = {}
  # ファイルの保存先のディレクトリ
  dir_dest = root + "/" + root[-20:]+"_json_n_txt/"
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
        # 保存先のディレクトリが存在しなかったらディレクトリを作成する
        if not os.path.exists(dir_dest):
          os.mkdir(dir_dest)
        # ファイルを書き込むためにtxtを開く
        with open(dir_dest + "{}.txt".format(dest_filebase), "w") as wf:
          # 書き込む
          if not x:
            # 一回目の書き込み
            wf.write(str(match_lc.group(1)) + "," + str(match_lc.group(2)) + "\n")
            lat, lon = (match_lc.group(1), match_lc.group(2))
            # ここであらかじめとり得る経度の値を保存しておく
            for i in range(11):
              # 国土地理院のデータは緯度経度から計算することで求められる
              tmp.append([lat, float(lon)+i*0.013])
          else:
            # 緯度経度を配列から取り出す
            # 経度はあらかじめ用意してあるものを使う
            lat, lon = float(tmp[-1][0]), float(tmp[count][1])
            # 緯度の計算に使う
            a = 0.0083333
            # 国土地理院のDEM5A(B)は縦10x横10の大きさなので横に10回読み込んだら1つ上に読み込む位置を変える
            if count == 11:
              # 丸める
              lat = round(lat+a, 9)
              # 書き込む横に10回読み込んだら経度を初期化する
              # 緯度を+aする
              wf.write(str(lat)+","+str(tmp[1][1])+"\n")
              # 緯度と経度を追加する　緯度だけでいいのだけれども
              tmp.append((lat, lon))
              count = 1
            else:
              wf.write(str(lat)+","+str(lon)+"\n")
          x = True
          count += 1
          print(count)
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

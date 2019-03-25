import re
import os
import sys

# マップの左下の位置
ptn_lc = re.compile(r"<gml:lowerCorner>(.*) (.*)</gml:lowerCorner>")
# ファイル名を抜き出す正規表現
ptn_file = re.compile(r"FG-GML-(.*)-(.*)-(.*)-.*-.*.xml")
# ファイルが保存してあるディレクトリ
root = os.path.dirname(os.path.abspath(sys.argv[0]))

def convert(filename):
  # ファイル名とマッチしているか
  match_file = ptn_file.match(os.path.basename(filename))
  # ファイル名
  dest_filebase = "{}".format(match_file.group(3))
  # ファイルの保存先のディレクトリ
  dir_dest = root + "/" + root[-21:-1] + "_txt/"
  # 保存先のディレクトリが存在しなかったらディレクトリを作成する
  if not os.path.exists(dir_dest):
    os.mkdir(dir_dest)
  # ファイルを書き込むためにtxtを開く
  with open(dir_dest + "{}.txt".format(dest_filebase), "w") as wf:
    # ファイルを開く
    with open(filename, encoding = "utf-8") as f:
      while True:
        # fファイルを一行ずつ読み込む
        line = f.readline()
        # lcとマッチするか
        match_lc = ptn_lc.search(line)
        if match_lc:
          # 書き込む
          wf.write(str(match_lc.group(1)) + "," + str(match_lc.group(2)) + "\n")
          break
    f.close()
  wf.close()

# root: 現在のディレクトリ dirs: root下に存在するディレクトリ files: root下に存在するファイル
for root, _, files in os.walk(root + "/"):
  for f in files:
    file_name = root + f
    convert(file_name)
    print(file_name)

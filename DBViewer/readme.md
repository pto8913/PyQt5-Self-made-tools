<img src="https://github.com/pto8913/PyQt5-s-tools/blob/master/Image/DBViewer.png" title="サンプル">

# ディレクトリ構成
root　- DBViewer.py <br>
　　　- DBViewerUI.py <br>
　　　- myfunc.py <br>
　　　- DBViwerDirSetting.py <br>

# サポート
- SQLite
(今後追加されるかもしれません)

# 使い方
データベースファイル(画像一番左)をダブルクリックすると <br>
そのデータベースのテーブルが(画像真ん中に)表示されます。 <br>
クエリの実行は画像右下の部分で行えます。 <br>

# 注意
明確に上限はわかりませんが、数百万件表示しようとしたところ、表示はできるものの表示途中に固まります。<br>
10万件 : 動作は重くなるものの、表示可能 <br>
1万件以下 : 問題なし <br>

# クエリの種類
SQLiteでできることはほぼ全部できるはず。

# データベースファイルの追加
ドラッグアンドドロップかAddボタンをクリックまたは、Ctrl+Oで行えます <br>

# データベースファイルの削除
すべて消したい場合はClearボタンかCtrl+Wで行えます <br>
任意の一つを削除したい場合は削除したいものを選択してDeleteボタンかDeleteで行えます <br>

# 終了
ExitボタンまたはEscで行えます <br>

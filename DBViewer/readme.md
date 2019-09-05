<img src="https://github.com/pto8913/PyQt5-s-tools/blob/master/Image/DBViewerQuery.png" title="サンプル">

# ディレクトリ構成
```PlainText
├── DB_dir
│   ├── database_file
│
└── DBViewer_dir
    ├── DBViewer.py
    └── DBViewer_dir
        ├── DBViewerUI.py
        ├── __init__.py
        ├── myfunc.py
        ├── DBViewerUIFunc.py
        └── DBViewerDirSetting.py
```


# 対応
- SQLite3

# 使い方
データベースファイル(画像一番左)をダブルクリックすると <br>
そのデータベースのテーブルが(画像真ん中に)表示されます  <br>
クエリの実行は画像右下のボタンか`Ctrl+Enter`で行えます <br>
画像のようにクエリを選択して実行もできます <br>

# 注意
明確に上限はわかりませんが、数百万件表示しようとしたところ、表示はできるものの表示途中に固まります <br>
10万件 : 動作は重くなるものの、表示可能 <br>
1万件以下 : 問題なし <br>

# クエリの種類？
SQLiteでできることはほぼ全部できるはず。 <br>
(一応 `select`, `create`, `drop`, `delete`, `alter`, `insert`, `pragma`) <br>
`Create database name`でDBディレクトリにデータベースファイルを作成できます <br>

# データベースファイルの追加
ドラッグアンドドロップかAddボタンをクリックまたは、Ctrl+Oで行えます <br>

# データベースファイルをリストから削除
すべて消したい場合はClearボタンかCtrl+Wで行えます <br>
任意の一つを削除したい場合は削除したいものを選択してDeleteボタンかDeleteで行えます <br>
(Noを押すとPCから消せます。) <br>

# 終了
ExitボタンまたはEscで行えます <br>


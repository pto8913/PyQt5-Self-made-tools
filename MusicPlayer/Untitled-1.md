# やあ
ごめんなさい
前投稿していたものがあり得ないレベルでゴミだったので修正しました。

今回は主にpygameを用いてミュージックプレイヤーを作るのを目標にやっていくよ

[コードだけ見たい人](#最後に全体を載せておくよ)

環境
* python3.7.4
* PyQt5.12.1

pygame公式ドキュメント
URL: https://www.pygame.org/docs/

PyQt5公式リファレンス
URL: https://doc.qt.io/qt-5.9/classes.html#e

##### まずはウィンドウを表示するところからだよ。

```python:MusicPlayer.py
import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QFont

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # DnD! DnD! DnD!
        self.setAcceptDrops(True)

        self.initUI()
  
    def initUI(self):
        # 左から画面 y座標 x座標 widget 縦サイズ 横サイズ
        self.setGeometry(300, 300, 700, 500)

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = Main()
    w.setWindowTitle('Music Player')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    # 動け～
    main()
```
うまくかけたかな？

##### 次はUIを作っていくよ
UIにはボタンやその機能、レイアウトを追加するよ

```python:MusicPlayerUI.py
from PyQt5.QtWidgets import QWidget, QPushButton

class MusicPlayerUI(QWidget):
    def initUI(self):
        # スタートボタンだよ
        startButton = QPushButton("Start")
        # 一時停止ボタンだよ
        self.pauseButton = QPushButton("Pause")
        # 次の曲にスキップするボタンだよ
        nextButton = QPushButton("Next")
        # 同じ曲だけを聴きたいときに使うボタンだよ
        self.loopButton = QPushButton("Loop")
        # 音楽を最初から流すときに使うボタンだよ
        resetButton = QPushButton("Reset")
        # クリックしたらミュージックプレイヤーが閉じちゃうよ。おそろしいね
        exitButton = QPushButton("Exit")

        self.setGeometry(300, 300, 700, 500)
```

これを`MusicPlayer.py`にimportして`MusicPlayer`に継承

```python:MusicPlayer.py
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

# MusicPlayerUI.py から MusicPlayerUIクラスを呼び出すよ
from MusicPlayerUI import MusicPlayerUI

class MusicPlayer(MusicPlayerUI):
    def __init__(self):
        super().__init__()
        self.initUI()

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = Main()
    w.setWindowTitle('Music Player')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    # 動け～
    main()
```

![2.png](https://qiita-image-store.s3.amazonaws.com/0/364882/2ff4553c-b11e-a562-c1b4-49ce6e3632dc.png)
わぁ、ボタンが一つしか出てないよー；；
なんて思わないでね。6個のボタンが重なってるだけだよ。
ボタンを作っただけでどこに置くか決めてないからこうなるんだよ。
ゆっくりやっていくから焦らないでね

もうすこしUIをいじるよ
##### ボタンを配置する場所を決めてあげるよ

```python:MusicPlayer.py
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QGridLayout

class MusicPlayerUI(QWidget):
    def initUI(self):
        startButton = QPushButton("Start")
        startButton.clicked.connect(self.startMusic)

        self.pauseButton = QPushButton("Pause")
        self.pauseButton.clicked.connect(self.pauseMusic)

        nextButton = QPushButton("Next")
        nextButton.clicked.connect(self.nextMusic)

        self.loopButton = QPushButton("Loop")
        self.loopButton.clicked.connect(self.loopMusic)
        
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.resetMusic)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.clickedExit)

        buttonlayout = QGridLayout()
        buttonlayout.addWidget(startButton, 0, 0)
        buttonlayout.addWidget(self.pauseButton, 0, 1)
        buttonlayout.addWidget(nextButton, 0, 2)
        buttonlayout.addWidget(self.loopButton, 1, 0)
        buttonlayout.addWidget(resetButton, 1, 1)
        buttonlayout.addWidget(exitButton, 1, 2)

        self.setLayout(layout)

        self.setGeometry(300, 300, 700, 500)
```
![3.png](https://qiita-image-store.s3.amazonaws.com/0/364882/7a3a76e2-5046-7153-c47b-957e1c6e367b.png)
うまく配置できたかな？
ボタンの位置を変えたいよー！って人は箱に入れる順番を変えてあげようね。
ちなみに`QGridLayout`という箱もあるよ。気になる人は調べてみよう！

##### 次はそれぞれのボタンに機能を追加していくよ。
ちょっと見づらくなるけど個別に作っていくよ。後で全体図を載せるから我慢してね
上のボタンから順番に作っていくよ
最初は `startButton`くん

```python:MusicPlayer.py
from pathlib import Path
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from MusicPlayerUI import MusicPlayerUI

class MusicPlayer(MusicPlayerUI):
    def __init__(self):
        super().__init__()

        # pygameモジュール全体の初期化をしてあげるよ
        pygame.init()
        # 道具を使いやすいようにしておくよ
        self.music = pygame.mixer.music
        self.loop = False

        self.PathInit()

        startButton.clicked.connect(self.startMusic)

        self.initUI()

    def startMusic(self):
        row = self.FileList.row(self.FileList.selectedItems()[0])
        self.music.load(str(self.FilePathList[row]))
        # 読み込んだファイルを再生するよ
        self.music.play(1)
        # あとでこの機能も作るよ
        self.isPause()
        # loopがTrueのとき処理が動くよ
        if self.loop:
            # あとでこの機能も作るよ
            self.resetMusic()
            return
        # pygameに新しいイベントを追加するよ
        # 音楽の再生が終わったっていうイベントだよ
        PLAY_END = pygame.USEREVENT+1
        # 音楽の再生が終わったら上で決めたイベントを起こすよ
        self.music.set_endevent(PLAY_END)
        # イベントが起きたか判断するよ
        check = True
        # while True:だよ。逮捕されちゃうね。怖いね
        while check:
        # pygameにもともとあるイベントととさっき作ったイベントを比べていくよ
        for event in pygame.event.get():
            # 音楽が終わっていたら処理が起こるよ
            if event.type == PLAY_END:
                # あとでこの機能も作るよ
                self.checkNext()
                # イベントが起きてるのがわかったからループから抜け出すよ
                check = False
                break
        # 次の音楽を流すよ
        self.startMusic()

    def PathInit(self):
        self.music_dir = Path().home.joinpath("music")

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = Main()
    w.setWindowTitle('Music Player')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()
```
スタートボタンに機能を追加したよ。いっぱいあってよくわからないかもしれないね。説明が下手でごめんね。

次は一時停止ボタン(pauseButton)くんに機能を追加するよ

```python:MusicPlayer.py
    def __init__(self):
        super().__init__()
        # 一時停止ボタンが押されたか判断するよ
        self.pause = True
        self.pauseButton.clicked.connect(self.pauseMusic)
        # ~~~ さっきと変わっていないところは省略するよ ~~~
        # 間違って消さないようにね


    def pauseMusic(self):
        # pauseがTrueなら一時停止、pauseがFalseなら止めた時間から再生するよ
        if self.pause:
            # 音楽を一時停止するよ
            self.music.pause()
            # 一時停止したよって教えてあげないとわからないから
            # 一時停止ボタンのテキストを書き換えてあげるよ
            self.pauseButton.setText("Clicked Pause")
            # 一時停止が押されたからFalseにしておくよ
            self.pause = False
        else:
            # 一時停止を解除するよ
            self.music.unpause()
            # pauseをTrueにして一時停止ボタンのテキストも書き換えてあげるよ
            self.isPause()


    def isPause(self):
        # 関数にしなくてもよくない？って思うよね。
        # あとで使う(かもしれない)からこれでいいんだよ。
        if not self.pause:
            self.pause = True
            self.pauseButton.setText("Pause?")      
```
ここまでが一時停止ボタンくんのすべてだよ

次は`nextButton`くんに機能を追加していくよ

```python:MusciPlayer.py
    def __init__(self):
        super().__init__()
        # ファイルの番号になるよ
        self.index = 0
        # ~~~ さっきと変わっていないところは省略するよ ~~~
        # 間違って消さないようにね
        # nextButtonをクリックすると処理が動くよ
        nextButton.clicked.connect(self.nextMusic)


    def nextMusic(self):
        # loopがTrueのとき動く処理だよ
        if self.loop:
            # 音楽を最初からにするよ。
            # loopするって言ってるんだから当然の動きだね
            self.resetMusic()
            # これ以降の処理をしないようにreturnしておくよ
            # else:を書いてもいいんだけどね。
            return
        # お、さっき関数にしておいてよかったね。コードの量が少しだけ短くなったよ(本当かな・・・)
        self.isPause()
        # 次の音楽が存在するか判断しているよ
        # 次の音楽がなかったら先頭の音楽に戻るよ
        self.checkNext()
        # 音楽を再生するよ
        self.startMusic()


    def checkNext(self):
        # 次の音楽が存在するか判断しているよ
        # 次の音楽がなかったら先頭の音楽に戻るよ
        if self.index+1 < len(self.FileList):
            self.index += 1
        else:
            self.index = 0
        # ファイルの名前を新しくしておかないとね
        self.fileName = self.FileList.item(self.index).text()
```
ここまでが`nextButton`くんのすべてだよ
次は`resetButton`くんだよ。

```python:MusicPlayer.py
    def __init__(self):
        super().__init__()
        # resetボタンがクリックされたら処理が動くよ
        resetButton.clicked.connect(self.resetMusic)


    def resetMusic(self):
        # 音楽を最初から再生するよ
        self.music.rewind()
```
短かったね。
次は`loopButton`くんと`exitButton`くんを一緒に書くよ。特に深い意味はないよ。

```python:MusciPlayer.py
    def __init__(self):
        super().__init__()
        # ループボタンがクリックされたら処理が動くよ
        self.loopButton.clicked.connect(self.loopMusic)
        # exitボタンがクリックされたらミュージックプレイヤーを閉じるよ
        exitButton.clicked.connect(self.clickedExit)

    
    def clickedExit(self):
        sys.exit()


    def loopMusic(self):
        # loopがTrueなら処理が動くよ
        if self.loop:
            # ループボタンのテキストを変えておくよ
            self.loopButton.setText("Loop?")
            # ループボタンが押されてない状態
            self.loop = False
        else:
            # 自分がループボタンを押したか覚えてられないから
            # テキストで分かりやすく教えてあげるよ
            self.loopButton.setText("Clicked Loop?")  
            # ループが押されたからループしてるよって意味でTrueに
            self.loop = True
```
ここまでが`loopButton`くんと`exitButton`くんのすべてだよ。
あれ？って思ったよね。
`FileList`を作っていなかったよ；；

`FileList`くんには`mp3`とか`m4a`とかを表示してもらうよ

```python:MusciPlayer.py
    def __init__(self):
        super().__init__()
        # ファイルの一覧を表示する箱を用意してあげるよ
        self.FileList = QListWidget()
        # ファイルのパスを保存する箱だよ
        self.FilePathList = []
        # 指定された形式のファイルだけを箱に入れてあげるよ
        self.setFileList()
        # 別のファイルをクリックしたとき処理が動くよ
        self.FileList.itemSelectionChanged.connect(self.FileListChanged)
        # まぁばれないでしょ～(ファイル名も用意するの忘れてた・・・)
        # 箱の中にあるファイルの名前をfileNameに入れておくよ
        self.fileName = ""

    
    def setFileList(self):
        # musicディレクトリ下にあって拡張子がmp3またはm4aのファイルのパスをリストに保存するよ
        for item in [f for f in self.music_dir.glob("**/*") if re.search(r".+\.(mp3|m4a)", f.name)]:
            self.FileList.addItem(item.name)
            self.FilePathList.append(item)


    def FileListChanged(self):
        # FileList上で選択してるファイルが変わったら新しく名前を受け取って
        # 音楽を再生するよ
        self.fileName = self.FileList.selectedItems()[0].text()
        self.startMusic()
```

##### 最後に全体を載せておくよ

```python:MusicPlayerUI.py
from PyQt5.QtWidgets import (
  QWidget, QGridLayout, QPushButton, QHBoxLayout
)

from pathlib import Path

class MusicPlayerUI(QWidget):
    def initUI(self):
        startButton = QPushButton("Start")
        startButton.clicked.connect(self.startMusic)

        self.pauseButton = QPushButton("Pause")
        self.pauseButton.clicked.connect(self.pauseMusic)

        nextButton = QPushButton("Next")
        nextButton.clicked.connect(self.nextMusic)

        self.loopButton = QPushButton("Loop")
        self.loopButton.clicked.connect(self.loopMusic)
        
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.resetMusic)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.clickedExit)

        buttonlayout = QGridLayout()
        buttonlayout.addWidget(startButton, 0, 0)
        buttonlayout.addWidget(self.pauseButton, 0, 1)
        buttonlayout.addWidget(nextButton, 0, 2)
        buttonlayout.addWidget(self.loopButton, 1, 0)
        buttonlayout.addWidget(resetButton, 1, 1)
        buttonlayout.addWidget(exitButton, 1, 2)

        layout = QHBoxLayout()
        layout.addWidget(self.FileList)
        layout.addLayout(buttonlayout)
        
        self.setLayout(layout)

        self.setGeometry(300, 300, 700, 500)
    
    # DnD! DnD! DnD!
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # DnD! DnD! DnD!
    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            x = Path(path)
            tmp = path.split('.')
            if x.name in self.FileList:
                continue
            if len(tmp) != 1:
                if x.suffix in ("mp3", "m4a"):
                    self.FileList.addItem(x.name)
                    self.FilePathList.append(x)
            else:
                self.addDir(Path(tmp[0]))

    # DnD! DnD! DnD!
    def addDir(self, item):
        for item in [f for f in self.music_dir.glob("**/*") if re.search(r".+\.(mp3|m4a)", f.name)]:
            self.FileList.addItem(item.name)
            self.FilePathList.append(item)
```


```python:MusicPlayer.py
import sys
import re
import pygame
from pathlib import Path
from PyQt5.QtWidgets import (
  QApplication, QListWidget,
)
from PyQt5.QtGui import QFont

from MusicPlayerUI import MusicPlayerUI

class MusicPlayer(MusicPlayerUI):
    def __init__(self, parent = None):
        super(MusicPlayer, self).__init__(parent)
        pygame.init()

        self.index = 0
        self.music = pygame.mixer.music

        self.setAcceptDrops(True)

        self.PathInit()
        self.pause = True
        self.loop = False

        self.FileList = QListWidget(self)
        self.FilePathList = []
        self.setFileList()
        self.FileList.itemSelectionChanged.connect(self.FileListChanged)
        self.fileName = ""
        
        self.initUI()

    def clickedExit(self):
        sys.exit()

    def loopMusic(self):
        if self.loop:
            self.loopButton.setText("Loop?")
            self.loop = False
        else:
            self.loopButton.setText("Clicked Loop?")  
            self.loop = True

    def startMusic(self):
        row = self.FileList.row(self.FileList.selectedItems()[0])
        self.music.load(str(self.FilePathList[row]))
        self.music.play(1)
        self.isPause()
        if self.loop:
            self.resetMusic()
            return
        PLAY_END = pygame.USEREVENT+1
        self.music.set_endevent(PLAY_END)
        tmp = True
        while tmp:
            for event in pygame.event.get():
                if event.type == PLAY_END:
                    self.checkNext()
                    tmp = False
                    break
        self.startMusic()

    def setFileList(self):
        for item in [f for f in self.music_dir.glob("**/*") if re.search(r".+\.(mp3|m4a)", f.name)]:
            self.FileList.addItem(item.name)
            self.FilePathList.append(item)

    def FileListChanged(self):
        self.fileName = self.FileList.selectedItems()[0].text()
        self.startMusic()

    def nextMusic(self):
        if self.loop:
            self.resetMusic()
            return
        self.isPause()
        self.checkNext()
        self.startMusic()

    def checkNext(self):
        if self.index+1 < len(self.FileList):
            self.index += 1
        else:
            self.index = 0
        self.fileName = self.FileList.item(self.index).text()

    def pauseMusic(self):
        if self.pause:
            self.music.pause()
            self.pauseButton.setText("Clicked Pause")
            self.pause = False
        else:
            self.music.unpause()
            self.isPause()

    def isPause(self):
        if not self.pause:
            self.pause = True
            self.pauseButton.setText("Pause?")

    def resetMusic(self):
        self.music.rewind()

    def PathInit(self):
        self.music_dir = Path().home().joinpath("music")

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Meiryo'))
    w = MusicPlayer()
    w.setWindowTitle('Music Player')
    w.show()
    w.raise_()
    app.exec_()

if __name__ == '__main__':
    main()
```
![7.png](https://qiita-image-store.s3.amazonaws.com/0/364882/e400f233-f218-0de2-9392-1cf24428ccdd.png)
どうかな。うまく機能してるかな？
最初はボリューム調節のためのスライダーも入れてたんだよ。
だけどね音の大きさが変わらなかったんだよ。だから消したよ。
ほかにも追加ボタンとかプレイリストとか、作りたい人は自分で作ってみよう！

ここまで読んでくれてありがとうございます。

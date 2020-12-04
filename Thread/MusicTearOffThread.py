from PyQt5.QtCore import QObject, pyqtSignal

from pathlib import Path
import subprocess
from scipy.io.wavfile import read
import numpy as np

class MusicTearOff(QObject):
    FinishedDelegate = pyqtSignal(np.ndarray)
    FailedDelegate = pyqtSignal(str)

    def __init__(
        self, 
        InputVideoPath: str,
        OutPutPath: str
    ):
        super(MusicTearOff, self).__init__()

        self.InputVideoPath = InputVideoPath
        self.OutPutMusicName = f"{OutPutPath}/{Path(InputVideoPath).name.split('.')[0]}.wav"

    def Start(self):
        print(f"Start  {self.OutPutMusicName}")
        command = f"ffmpeg -i {self.InputVideoPath} {self.OutPutMusicName}"
        subprocess.call(command, shell=True)

        if not Path(self.OutPutMusicName).exists():
            self.FailedDelegate.emit(str(self.InputVideoPath))
            return

        _, AudioData = read(self.OutPutMusicName)

        self.FinishedDelegate.emit(AudioData)

    
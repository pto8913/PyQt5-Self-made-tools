import sqlite3
from pathlib import Path
import cv2

import threading
import queue
import subprocess
from scipy.io.wavfile import read

# p = Path("C:/Users/black/Videos/")
# conn = sqlite3.connect(str(p) + "/Test.db")
# cur = conn.cursor()
# conn.close()

class MainProcess:
    def __init__(self):
        self.Path = Path("C:/Users/black/Videos/")
        self.Tasks = queue.Queue()

        self.conn = sqlite3.connect(str(self.Path) + "/Test.db")
        print(str(self.Path) + "Test.db")
        self.cur = self.conn.cursor()

        self.cur.execute("create table if not exists A(Name str, VideoData blob, AudioData blob)")
        self.conn.commit()

    def Start(self):
        
        for elem in self.Path.glob("**/*.mp4"):
            self.Tasks.put(elem)
        
        NumOfTask = self.Tasks.qsize()
        self.Result = [0 for _ in range(NumOfTask)]
        Thread = threading.Thread(target=self.OutputAudioThread)
        Thread.start()
        
        
        self.Tasks.join()

        for _ in range(NumOfTask):
            self.Tasks.put(None)

        print("Finished All Tasks")

        self.conn.close()

    def OutputAudioThread(self):
        self.CurrentTaskPath = self.Tasks.get()
        if self.CurrentTaskPath is None:
            return
        self.OutputAudioName = f"C:/Users/black/Videos/{self.CurrentTaskPath.name.split('.')[0]}.wav"
        command = f"ffmpeg -i {str(self.CurrentTaskPath)} {self.OutputAudioName}"
        subprocess.call(command, shell=True)
        
        _, AudioData = read(self.OutputAudioName)

        Capture = cv2.VideoCapture(str(self.CurrentTaskPath))
        _, VideoData = Capture.read()

        self.cur.execute(f"""
            insert into A (Name, VideoData, AudioData) Values (
                {Path(self.OutputAudioName).name.split('.')[0]},
                {VideoData},
                {AudioData}
            )"""
        )
        self.conn.commit()
        
        try:
            Path(self.OutputAudioName).unlink()
        except:
            pass

        self.Tasks.task_done()
        

p = MainProcess()
p.Start()

# p.Init()
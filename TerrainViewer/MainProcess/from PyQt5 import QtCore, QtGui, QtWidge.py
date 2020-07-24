from PyQt5 import QtCore, QtGui, QtWidgets
import queue
import time

class Signal(QtCore.QObject):
    sig = QtCore.pyqtSignal(int)

class Worker(QtCore.QRunnable):
    def __init__(self, theQueue, sig):
        QtCore.QRunnable.__init__(self)
        self.theQueue = theQueue
        self.signal = sig

    def run(self):
        while True:
            task = self.theQueue.get()
            if task is None:
                self.theQueue.task_done()
                return
            time.sleep(1)
            print(task)
            self.signal.sig.emit(int(task))
            self.theQueue.task_done()

def result_callback(result):
    print("Got {}".format(result))

MAX_THREADS = 2
def launch_threads():
    theQueue = queue.Queue()
    pool = QtCore.QThreadPool()
    pool.setMaxThreadCount(MAX_THREADS)
    for task in range(MAX_THREADS): 
        sig = Signal()
        sig.sig.connect(result_callback)
        pool.start(Worker(theQueue, sig))

    for i in range(MAX_THREADS * 6): # Sending more values than there are threads
        theQueue.put(i)

    # Tell the threads in the pool to finish
    for i in range(MAX_THREADS):
        theQueue.put(None)

    pool.waitForDone()

    print("Finished")

    QtCore.QTimer.singleShot(0, QtWidgets.QApplication.instance().exit)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    QtCore.QTimer.singleShot(0, launch_threads)
    app.exec_()
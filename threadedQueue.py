import threading
import time
from queue import Queue

class ThreadedQueue(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self)
    self.q = Queue()
    self.kill = False

  def run(self):
    while self.kill == False:
      if(self.q.empty()==False):
        message = self.q.get()
        self.handleMessage(message)
      self.work()
      time.sleep(0.00001)


  def handleMessage(self, message):
    pass

  def work(self):
    pass

  def sendMessage(self,message):
    self.q.put(message)

  def doKill(self):
    self.kill = True

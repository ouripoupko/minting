import threading
import time
from queue import Queue


class ThreadedQueue(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self)
    self.q = Queue()
    self.lock = threading.Lock()
    self.kill = False
    

  def run(self):
    while self.kill == False:
      self.lock.acquire()
      if(self.q.empty()==False):
        message = self.q.get()
        self.handleMessage(message)
        self.q.task_done()
      else:
        time.sleep(0.01)
      self.work()
      self.lock.release()
      time.sleep(0.00001)


  def handleMessage(self, message):
    pass

  def work(self):
    pass

  def sendMessage(self,message):
    self.q.put(message)

  def pause(self):
    self.lock.acquire()
    
  def release(self):
    self.lock.release()
    
  def doKill(self):
    self.kill = True

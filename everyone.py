
from threadedQueue import ThreadedQueue

from honest import Honest
from corrupt import Corrupt
from sybil import Sybil
import random
import math

HONEST, CORRUPT, SYBIL = range(3)
class Everyone(ThreadedQueue):

  def __init__(self,settings):
    ThreadedQueue.__init__(self)
    self.settings = settings
    self.counters = [0,0,0]
    self.constructor = [Honest,Corrupt,Sybil]
    self.community={}
    self.idCount = 1
    self.readyCount = 0
    self.loops = 0
    random.seed()

  def handleMessage(self, message):
    if message["msg"] == "connect":
      self.findFriend(message["sender"])
    if message["msg"] == "ready":
      if(self.loops == 0):
        print("ready with neighbours:", self.readyCount)
      self.readyCount = self.readyCount + 1

  def work(self):
    if math.floor(self.counters[CORRUPT]*self.settings.sybilRatio) > self.counters[SYBIL]:
      idType = SYBIL
    elif math.floor(self.counters[HONEST]*self.settings.corruptRatio) > self.counters[CORRUPT]:
      idType = CORRUPT
    elif self.settings.honests > self.counters[HONEST]:
      idType = HONEST
    else:
      idType = -1
    if idType != -1:
      self.community[self.idCount] = self.constructor[idType](self.settings,self.idCount,self)
      self.community[self.idCount].start()
      self.counters[idType] = self.counters[idType]+1
      self.idCount = self.idCount + 1
    if self.readyCount == len(self.community):
      self.readyCount = 0
      if self.loops > 100:
        for identity in self.community.values():
          identity.sendMessage({"msg":"die"})
        self.doKill()
      else:
        self.loops = self.loops + 1
        print("minting loops:",self.loops)
        for identity in self.community.values():
          identity.sendMessage({"msg":"mint"})

  def findFriend(self, identity):
    someone = random.choice(list(self.community.values()))
    identity.sendMessage({"msg":"befriend", "friend":someone})


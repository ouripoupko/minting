
from threadedQueue import ThreadedQueue

from honest import Honest
from corrupt import Corrupt
from sybil import Sybil
import random
import math
import time

HONEST, CORRUPT, SYBIL = range(3)
identType = {Honest:HONEST,Corrupt:CORRUPT,Sybil:SYBIL}

class Everyone(ThreadedQueue):

  def __init__(self,settings):
    ThreadedQueue.__init__(self)
    self.settings = settings
    self.counters = [0,0,0]
    self.constructor = [Honest,Corrupt,Sybil]
    self.community={}
    self.bootstrap = []
    self.dead = []
    self.idCount = 1
    self.ready = {}
    self.maxReady = 0
    self.loops = 0
    self.payments = 0
    self.attempts = 0
    self.reports = 0
    random.seed()

  def handleMessage(self, message):
    if message["msg"] == "connect":
      self.findFriend(message["sender"])
    if message["msg"] == "ready":
      sender = message["sender"]
      self.ready[sender.getID()] = sender
      if(self.loops == 0):
        if len(self.ready) > self.maxReady:
          self.maxReady = len(self.ready)
          print("ready with neighbours:", self.maxReady)
    if message["msg"] == "unfold":
      sender = message["sender"]
      self.ready.pop(sender.getID(),None)
    if message["msg"] == "died":
      dead = message["sender"]
      self.dead.append(self.community.pop(dead.getID(),None))
      self.counters[identType[type(dead)]] = self.counters[identType[type(dead)]]-1
      if "payments" in message:
        self.payments = self.payments + message["payments"]
    if message["msg"] == "payments":
      self.payments = self.payments + message["payments"]
    if message["msg"] == "report":
      self.reports = self.reports + message["minted"]

  def work(self):
    if math.floor(self.counters[CORRUPT]*self.settings.sybilRatio) > self.counters[SYBIL]:
      idType = SYBIL
    elif math.floor(self.counters[HONEST]*self.settings.corruptRatio) > self.counters[CORRUPT]:
      idType = CORRUPT
    elif self.settings.honests > self.counters[HONEST]:
      idType = HONEST
    else:
      idType = -1
    if idType == -1:
      for identity in self.bootstrap:
        identity.sendMessage({"msg":"start"})
      self.bootstrap = []
    else:
      print("Creating a new identity",self.idCount)
      self.community[self.idCount] = self.constructor[idType](self.settings,self.idCount,self,self.loops)
      self.community[self.idCount].start()
      self.bootstrap.append(self.community[self.idCount])
      self.counters[idType] = self.counters[idType]+1
      self.idCount = self.idCount + 1
    if len(self.ready) == len(self.community) and self.payments == 0:
      self.attempts = 0
      self.ready = {}
      if self.loops == self.settings.rounds:
        for identity in self.community.values():
          identity.sendMessage({"msg":"die"})
          time.sleep(0.1)
        for identity in sorted(self.dead, key = lambda ident: ident.getID()):
          identity.sendMessage({"msg":"die"})
          time.sleep(0.1)
        self.doKill()
      else:
        self.loops = self.loops + 1
        print("minting loops:",self.loops, "minted:",self.reports,sep=",")
        self.reports = 0
        for identity in self.community.values():
          identity.sendMessage({"msg":"mint"})
    self.attempts = self.attempts + 1
    if self.attempts == 5000:
      import pdb; pdb.set_trace()

  def findFriend(self, identity):
    someone = random.choice(list(self.community.values()))
    identity.sendMessage({"msg":"befriend", "friend":someone})


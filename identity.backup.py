
from stateMachine import State, StateMachine

class Init(State):
  def next(self,message):
    super().next(message)
    if message["msg"] == "start":
      return [Idle(self.sm), self.onStart]

  def onStart(self):
    print(self, "start transition")

class Idle(State):
  pass

class Identity(StateMachine):
  def __init__(self,settings,myid,everyone,loop):
    StateMachine.__init__(self)
    self.state = Init(self)
    self.settings = settings
    self.id=myid
    self.everyone=everyone
    self.loop = loop

  def __str__(self):
    return type(self).__name__+"-"+str(self.id)







'''from threadedQueue import ThreadedQueue
import random
import bisect
import copy

INIT, IDLE, WAIT_FRIEND, WAIT_APPROVE, READY, MINTING, DEAD = range(7)
MINTED, NEIGHBOURS, FINE, START, END = range(5)
class Identity(ThreadedQueue):

  def __init__(self,settings,myid,everyone,loop):
    ThreadedQueue.__init__(self)
    self.settings = settings
    self.id=myid
    self.everyone=everyone
    self.state = INIT
    self.loop = loop
    self.ledger = [{MINTED:0,NEIGHBOURS:{},FINE:0, START:self.loop, END:self.loop}]
    self.ledgerIndex = [0]
    self.exposedMessages = []
    self.attempts = 0

  def __str__(self):
    return type(self).__name__+"-"+str(self.id)

  def handleMessage(self, message):
    if message["msg"] == "befriend" and self.state == WAIT_FRIEND:
      candidate = message["friend"]
      if candidate != self and self.isAFriend(candidate) and candidate not in self.ledger[-1][NEIGHBOURS].values():
        candidate.sendMessage({"msg":"directConnect","sender":self})
        self.state = WAIT_APPROVE
      else:
        self.state = IDLE
    if message["msg"] == "directConnect":
      sender = message["sender"]
      if self.state == WAIT_APPROVE or len(self.ledger[-1][NEIGHBOURS]) > self.settings.d:
        sender.sendMessage({"msg":"decline"})
      else:
        if self.loop > self.ledger[-1][START]:
          self.ledgerIndex.append(self.loop)
          self.ledger.append({MINTED:0,NEIGHBOURS:self.ledger[-1][NEIGHBOURS].copy(),FINE:0, START:self.loop, END:self.loop})
        self.ledger[-1][NEIGHBOURS][sender.getID()] = sender
        self.attempts = 0
        self.state = IDLE if self.state != READY else READY
        sender.sendMessage({"msg":"connected", "sender":self})
    if message["msg"] == "decline":
      self.state = IDLE
    if message["msg"] == "connected":
      sender = message["sender"]
      self.ledger[-1][NEIGHBOURS][sender.getID()] = sender
      self.attempts = 0
      self.state = IDLE
    if message["msg"] == "mint":
      self.state = MINTING
    if message["msg"] == "die":
      self.doKill()
    if message["msg"] == "exposed":
      self.exposedMessages.append(message)
    if message["msg"] == "start":
      self.state = IDLE

  def work(self):
    if self.state == IDLE or self.state == DEAD:
      if self.exposedMessages:
        if self.state == IDLE:
          self.ledgerIndex.append(self.loop)
          self.ledger.append({MINTED:0,NEIGHBOURS:self.ledger[-1][NEIGHBOURS].copy(),FINE:0, START:self.loop, END:self.loop})
        for message in self.exposedMessages:
          self.handleExposed(message)
        self.exposedMessages = []
    if self.state == IDLE:
      if len(self.ledger[-1][NEIGHBOURS]) < self.settings.d:
        self.attempts = self.attempts+1
        if self.attempts > 100:
          print(self,"failed attempts",self.attempts)
          import pdb; pdb.set_trace()
        self.everyone.sendMessage({"msg":"connect","sender":self})
        self.state = WAIT_FRIEND
      else:
        self.everyone.sendMessage({"msg":"ready","sender":self})
        self.state = READY
    if self.state == MINTING:
      self.ledger[-1][MINTED] = self.ledger[-1][MINTED] + 1
      self.ledger[-1][END] = self.loop
      self.age()
      if self.state != DEAD:
        self.state = IDLE
        self.loop = self.loop + 1

  def handleExposed(self, message):
    if self.state == IDLE:
      self.ledger[-1][NEIGHBOURS].pop(message["sender"].getID(),None)
    start = message["start"]
    end = message["end"]
    stop = start
    fine = message["fine"]/(end+1-start)
    while stop<end+1:
      index = bisect.bisect_right(self.ledgerIndex, start)-1
      stop = min(self.ledger[index][END],end)+1
      if stop <= start:
        break
      if self.state == IDLE:
        self.ledger[index][FINE] = fine*(stop-start)
      else:
        print(self,[ident.getID() for ident in self.ledger[index][NEIGHBOURS].values()],start,stop,end,self.ledger[index][END])
        for neighbour in self.ledger[index][NEIGHBOURS].values():
          if neighbour not in message["visited"]:
            neighbour.sendMessage({"msg":"exposed",
                                   "sender":self,
                                   "visited":message["visited"]+[self],
                                   "start":start,
                                   "end":stop-1,
                                   "fine":fine*(stop-start)})
      start = stop


  def isAFriend(self, identity):
    pass

  def age(self):
    pass

  def isAvailable(self):
    return len(self.ledger[-1][NEIGHBOURS]) < self.settings.d + 1

  def getID(self):
    return self.id

  def doKill(self):
    print(self,self.ledger)
    super().doKill()
'''


from threadedQueue import ThreadedQueue
import random

IDLE, WAIT_FRIEND, WAIT_APPROVE, READY, MINTING = range(5)
class Identity(ThreadedQueue):

  def __init__(self,settings,myid,everyone):
    ThreadedQueue.__init__(self)
    self.settings = settings
    self.id=myid
    self.everyone=everyone
    self.neighbours = {}
    self.state = IDLE
    self.minted = 0

  def __str__(self):
    return type(self).__name__+"-"+str(self.id)

  def handleMessage(self, message):
    if message["msg"] == "befriend" and self.state == WAIT_FRIEND:
      candidate = message["friend"]
      if candidate != self and self.isAFriend(candidate):
        candidate.sendMessage({"msg":"directConnect","sender":self})
        self.state = WAIT_APPROVE
      else:
        self.state = IDLE
    if message["msg"] == "directConnect":
      sender = message["sender"]
      if self.state == WAIT_APPROVE or len(self.neighbours) > self.settings.d:
        sender.sendMessage({"msg":"decline"})
      else:
        self.neighbours[sender.getID()] = sender
        self.state = IDLE if self.state != READY else READY
        sender.sendMessage({"msg":"connected", "sender":self})
    if message["msg"] == "decline":
      self.state = IDLE
    if message["msg"] == "connected":
      sender = message["sender"]
      self.neighbours[sender.getID()] = sender
      self.state = IDLE
    if message["msg"] == "mint":
#      print(self, self.neighbours.keys())
      self.state = MINTING
    if message["msg"] == "die":
      self.doKill()

  def work(self):
    if self.state == IDLE:
      if len(self.neighbours) < self.settings.d:
        self.everyone.sendMessage({"msg":"connect","sender":self})
        self.state = WAIT_FRIEND
      else:
        self.everyone.sendMessage({"msg":"ready","sender":self})
#        print(self, "ready")
        self.state = READY
    if self.state == MINTING:
      self.minted = self.minted + 1
      self.age()
      self.state = IDLE

  def isAFriend(self, identity):
    pass

  def age(self)
    None

  def isAvailable(self):
    return len(self.neighbours) < self.settings.d + 1

  def getID(self):
    return self.id

  def doKill(self):
    print(self,self.minted)
    super().doKill()


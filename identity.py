
from stateMachine import State, StateMachine
import bisect

class Unexpected(State):
  def actionOnEntry(self):
    print(self, "!!!   unexpected message arrived   !!!",message)
    return [None, None]


class Alive(State):
  def next(self,message):
    if message["msg"] == "die":
      self.sm.doKill()
      return [None, None]
    return [Unexpected(self.sm,message),None]


class Init(State):
  def next(self,message):
    if message["msg"] == "start":
      return [Idle(self.sm,message), None]
    return [Unexpected(self.sm,message),None]


class Idle(Alive):
  def next(self,message):
    if message["msg"] == "directConnect":
      return [AcceptFriend(self.sm,message),None]
    return super().next(message)


class WaitFriend(Alive):
  def next(self,message):
    if message["msg"] == "befriend"
      return [InspectFriend(self.sm,message),None]
    if message["msg"] == "directConnect":
      return [AcceptFriend(self.sm,message),None]
    return super().next(message)


class InspectFriend(Condition):
  def resolve(self):
    candidate = self.message["friend"]
    if candidate != self.sm and self.sm.isAFriend(candidate) and candidate not in self.getNeighbours():
      candidate.sendMessage({"msg":"directConnect","sender":self.sm})
      return [WaitApprove(self.sm,message),None]
    return [Idle(self.sm,message),None]


class WaitApprove(Alive):
  def next(self,message):
    if message["msg"] == "directConnect":
      sender = self.message["sender"]
      sender.sendMessage({"msg":"decline"})
      return [None,None]
    if message["msg"] == "decline":
      return [Idle(self.sm,message),None]
    if message["msg"] == "connected":
      sender = message["sender"]
      self.sm.addNeighbour(sender)
      return [Idle(self.sm,message),None]
    return super().next(message)


class AcceptFriend(Alive):
  def ActionOnEntry(self):
    sender = self.message["sender"]
    if len(self.sm.getNeighbours()) > self.sm.getSettings.d:
      sender.sendMessage({"msg":"decline"})
    else:
      self.sm.growLedger()
      self.sm.addNeighbour(sender)
      sender.sendMessage({"msg":"connected", "sender":self.sm})
    return [Idle(self.sm),None]


class Ready(Alive):
  def next(self,message):
    if message["msg"] == "directConnect":
      return [AcceptFriend(self.sm,message),self.UnfoldReadiness]
    if message["msg"] == "mint":
      return [Minting(self.sm,message),None]
    return super().next(message)

  def UnfoldReadiness(self):
    self.sm.sendMessage({"msg":"unfold"})


class Minting(Alive):
  pass


class Dead(Alive):
  pass

MINTED, NEIGHBOURS, FINE, START, END = range(5)

class Identity(StateMachine):
  def __init__(self,settings,myid,everyone,loop):
    StateMachine.__init__(self)
    self.state = Init(self)
    self.settings = settings
    self.id=myid
    self.everyone=everyone
    self.loop = loop
    self.ledger = [{MINTED:0,NEIGHBOURS:{},FINE:0, START:self.loop, END:self.loop}]
    self.ledgerIndex = [0]

  def __str__(self):
    return type(self).__name__+"-"+str(self.id)

  def getNeighbours(self):
    return self.ledger[-1][NEIGHBOURS].values()

  def getSettings(self):
    return self.settings

  def growLedger(self):
    if self.loop > self.ledger[-1][START]:
      self.ledgerIndex.append(self.loop)
      self.ledger.append({MINTED:0,NEIGHBOURS:self.ledger[-1][NEIGHBOURS].copy(),FINE:0, START:self.loop, END:self.loop})

  def addNeighbour(self,neighbour):
    self.ledger[-1][NEIGHBOURS][neighbour.getID()] = neighbour

  def doKill(self):
    print(self,self.ledger)
    super().doKill()


'''from threadedQueue import ThreadedQueue

    self.exposedMessages = []
    self.attempts = 0

  def handleMessage(self, message):
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

'''

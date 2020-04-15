
from stateMachine import State, StateMachine
import bisect

class Unexpected(State):
  def actionOnEntry(self):
    print(self, "!!!   unexpected message arrived   !!!",self.message)
    return [None, None]


class Alive(State):
  def next(self,message):
    if message["msg"] == "exposed":
      self.sm.addExposed(message)
      return [self,None]
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

  def actionOnEntry(self):
    self.sm.handleExposed(True)
    if len(self.sm.getNeighbours()) < self.sm.getSettings().d:
      self.sm.getEveryone().sendMessage({"msg":"connect","sender":self.sm})
      return [WaitFriend(self.sm),None]
    self.everyone.sendMessage({"msg":"ready"})
    return [Ready(self.sm),None]


class WaitFriend(Alive):
  def next(self,message):
    if message["msg"] == "befriend":
      candidate = message["friend"]
      if candidate != self.sm and self.sm.isAFriend(candidate) and candidate not in self.sm.getNeighbours():
        candidate.sendMessage({"msg":"directConnect","sender":self.sm})
        return [WaitApprove(self.sm,message),None]
      else:
        return [Idle(self.sm,message),None]
    if message["msg"] == "directConnect":
      return [AcceptFriend(self.sm,message),None]
    return super().next(message)


class WaitApprove(Alive):
  def next(self,message):
    if message["msg"] == "directConnect":
      sender = message["sender"]
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
    if len(self.sm.getNeighbours()) > self.sm.getSettings().d:
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
  def actionOnEntry(self):
    self.sm.mint()
    return [Idle(self.sm),None]


class Dead(Alive):
  def actionOnEntry(self):
    self.sm.handleExposed(False)
    return [None,None]


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
    self.exposedMessages = []

  def __str__(self):
    return type(self).__name__+"-"+str(self.id)

  def getNeighbours(self):
    return self.ledger[-1][NEIGHBOURS].values()

  def getSettings(self):
    return self.settings

  def getEveryone(self):
    return self.everyone

  def growLedger(self):
    if self.loop > self.ledger[-1][START]:
      self.ledgerIndex.append(self.loop)
      self.ledger.append({MINTED:0,NEIGHBOURS:self.ledger[-1][NEIGHBOURS].copy(),FINE:0, START:self.loop, END:self.loop})

  def addNeighbour(self,neighbour):
    self.ledger[-1][NEIGHBOURS][neighbour.getID()] = neighbour

  def addExposed(self,message):
    self.exposedMessages.append(message)

  def isAFriend(self, identity):
    pass

  def age(self):
    pass

  def isAvailable(self):
    return len(self.getNeighbours()) <= self.settings.d

  def getID(self):
    return self.id

  def mint(self):
    self.ledger[-1][MINTED] = self.ledger[-1][MINTED] + 1
    self.ledger[-1][END] = self.loop
    self.age()
    self.loop = self.loop + 1

  def handleExposed(self, bHandleNeighbours):
    bGrowLedger = False
    if self.exposedMessages:
      if bHandleNeighbours:
        bGrowLedger = True;
    for message in self.exposedMessages:
      if bHandleNeighbours:
        if message["sender"].getID() in self.ledger[-1][NEIGHBOURS]:
          if bGrowLedger:
            self.growLedger()
            bGrowLedger = False
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
        if bHandleNeighbours:
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
    self.exposedMessages = []

  def doKill(self):
    print(self,self.ledger)
    super().doKill()



from stateMachine import State, StateMachine
import bisect
import random
import time


class Unexpected(State):
  def actionOnEntry(self):
    print(self, "!!!   unexpected message arrived   !!!",self.message)
    return [None, None]


class Alive(State):
  def next(self,message):
    if message["msg"] == "befriend":
      # ditch this message as I probably got a friend contacting me while waiting to contact a friend
      return [None,None]
    if message["msg"] == "directRequest":
      sender = message["sender"]
      sender.sendMessage({"msg":"decline"})
      return [None,None]
    if message["msg"] == "pay":
      self.sm.acceptPayment(message["amount"],message["start"],message["end"])
      return [None, None]
    if message["msg"] == "done":
      self.sm.getDeadNotifiers().pop(message["sender"],None)
      return [None, None]
    if message["msg"] == "died":
      self.sm.addDied(message)
      return [None,None]
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
    if message["msg"] == "directRequest":
      return [AcceptDirect(self.sm,message),None]
    if message["msg"] == "died":
      self.sm.addDied(message)
      return [self,None]
    if message["msg"] == "pay":
      self.sm.acceptPayment(message["amount"],message["start"],message["end"])
      return [self, None]
    if message["msg"] == "done":
      self.sm.getDeadNotifiers().pop(message["sender"],None)
      return [self, None]
    return super().next(message)

  def actionOnEntry(self):
    self.sm.handleDied(True)
    if self.sm.getDeadNotifiers():
      return [None,None]
    if len(self.sm.getNeighbours()) < self.sm.getSettings().d:
      self.sm.getEveryone().sendMessage({"msg":"connect","sender":self.sm})
      return [WaitFriend(self.sm),None]
    return [Ready(self.sm),None]


class WaitFriend(Alive):
  def next(self,message):
    if message["msg"] == "befriend":
      candidate = message["friend"]
      if candidate != self.sm and self.sm.isAFriend(candidate) and candidate not in self.sm.getNeighbours().values():
        candidate.sendMessage({"msg":"directRequest","sender":self.sm,"request":"add"})
        return [WaitApprove(self.sm,message),None]
      else:
        return [Idle(self.sm,message),None]
    if message["msg"] == "directRequest":
      return [AcceptDirect(self.sm,message),None]
    return super().next(message)


class WaitApprove(Alive):
  def next(self,message):
    if message["msg"] == "decline":
      return [Idle(self.sm,message),None]
    if message["msg"] == "accept":
      sender = message["sender"]
      self.sm.addNeighbour(sender)
      return [Idle(self.sm,message),None]
    return super().next(message)


class AcceptDirect(Alive):
  def actionOnEntry(self):
    sender = self.message["sender"]
    request = self.message["request"]
    if request == "add" and len(self.sm.getNeighbours()) <= self.sm.getSettings().d:
      self.sm.growLedger()
      oldNeighbours = list(self.sm.getNeighbours().values())
      self.sm.addNeighbour(sender)
      sender.sendMessage({"msg":"accept", "sender":self.sm})
      if len(self.sm.getNeighbours()) > self.sm.getSettings().d:
        random.shuffle(oldNeighbours)
        return [ReduceEdges(self.sm, oldNeighbours),None]
    elif request == "remove" and len(self.sm.getNeighbours()) > self.sm.getSettings().d:
      self.sm.growLedger()
      self.sm.removeNeighbour(sender)
      sender.sendMessage({"msg":"accept", "sender":self.sm})
    else:
      sender.sendMessage({"msg":"decline"})
    return [Idle(self.sm),None]


class ReduceEdges(Alive):
  def next(self,message):
    if message["msg"] == "decline":
      return [self, None]
    if message["msg"] == "accept":
      self.sm.removeNeighbour(message["sender"])
      return [Idle(self.sm),None]
    return super().next(message)

  def actionOnEntry(self):
    if len(self.message) > 0:
      candidate = self.message.pop()
      candidate.sendMessage({"msg":"directRequest","sender":self.sm,"request":"remove"})
    else:
      return [Idle(self.sm),None]
    return [None, None]


class Ready(Alive):
  def next(self,message):
    if message["msg"] == "directRequest":
      return [AcceptDirect(self.sm,message),None]
    if message["msg"] == "died":
      self.sm.addDied(message)
      return [Idle(self.sm,message),None]
    if message["msg"] == "mint":
      return [Minting(self.sm,message),None]
    return super().next(message)

  def actionOnEntry(self):
    self.sm.getEveryone().sendMessage({"msg":"ready","sender":self.sm})
    return [None,None]
  def actionOnExit(self):
    self.sm.getEveryone().sendMessage({"msg":"unfold","sender":self.sm})


class Minting(Alive):
  def actionOnEntry(self):
    if self.sm.mint():
      return [Idle(self.sm),None]
    else:
      return [Dead(self.sm),None]


class Dead(Alive):
  def next(self,message):
    if message["msg"] == "died":
      self.sm.addDied(message)
      return [self,None]
    if message["msg"] == "pay":
      self.sm.acceptPayment(message["amount"],message["start"],message["end"])
      return [self,None]
    if message["msg"] == "done":
      self.sm.getDeadNotifiers().pop(message["sender"],None)
      return [self,None]
    if message["msg"] == "guilty":
      self.sm.CollectReplies(message)
      return [self,None]
    return super().next(message)

  def actionOnEntry(self):
    self.sm.handleDied(False)
    return [None,None]


MINTED, NEIGHBOURS, FINE, PAID, START, END = range(6)

class Identity(StateMachine):
  def __init__(self,settings,myid,everyone,loop):
    StateMachine.__init__(self)
    self.state = Init(self)
    self.settings = settings
    self.id=myid
    self.everyone=everyone
    self.loop = loop
    self.ledger = [{MINTED:0,NEIGHBOURS:{},FINE:0, PAID:0, START:self.loop, END:self.loop}]
    self.ledgerIndex = [0]
    self.diedMessages = []
    self.deadNotifiers = {}

  def __str__(self):
    return type(self).__name__+"-"+str(self.id)

  def __repr__(self):
    return type(self).__name__+"-"+str(self.id)

  def getNeighbours(self):
    return self.ledger[-1][NEIGHBOURS]

  def getSettings(self):
    return self.settings

  def getEveryone(self):
    return self.everyone

  def growLedger(self):
    if self.loop > self.ledger[-1][START]:
      self.ledgerIndex.append(self.loop)
      self.ledger.append({MINTED:0,NEIGHBOURS:self.ledger[-1][NEIGHBOURS].copy(),FINE:0, PAID:0, START:self.loop, END:self.loop})

  def addNeighbour(self,neighbour):
    self.ledger[-1][NEIGHBOURS][neighbour.getID()] = neighbour

  def removeNeighbour(self,neighbour):
    self.ledger[-1][NEIGHBOURS].pop(neighbour.getID(),None)

  def addDied(self,message):
    self.diedMessages.append(message)

  def isAFriend(self, identity):
    pass

  def age(self):
    return True

  def isAvailable(self):
    return len(self.getNeighbours()) <= self.settings.d

  def getID(self):
    return self.id
    
  def getDeadNotifiers(self):
    return self.deadNotifiers

  def mint(self):
    self.ledger[-1][MINTED] = self.ledger[-1][MINTED] + 1
    amount = 1
    for record in self.ledger:
      if record[FINE] > 0:
        payment = min(record[FINE], amount)
        record[PAID] = record[PAID] + payment
        record[FINE] = record[FINE] - payment
        amount = amount - payment
      if amount == 0:
        break
    self.everyone.sendMessage({"msg":"report","minted":1-(1-amount)/2})
    self.ledger[-1][END] = self.loop
    self.loop = self.loop + 1
    return self.age()

  def handleDiedWhenDead(self,message):
    pass
    
  def handleDied(self, bIsAlive):
    bGrowLedger = True
    for message in self.diedMessages:
      if "start" in message:
        if message["dead"] not in self.deadNotifiers:
          self.deadNotifiers[message["dead"]] = {"start":[message["start"]],"end":[message["end"]]}
        else:
          first = bisect.bisect_left(self.deadNotifiers[message["dead"]]["start"],message["start"])
          if first == len(self.deadNotifiers[message["dead"]]["start"]):
            if self.deadNotifiers[message["dead"]]["end"][first-1] >= message["end"]:
              message["dead"].sendMessage({"msg":"guilty","sender":self,"payments":0,"start":message["start"],"end":message["end"]})
              continue
            self.deadNotifiers[message["dead"]]["start"].append(message["start"])
            self.deadNotifiers[message["dead"]]["end"].append(message["end"])
            if self.deadNotifiers[message["dead"]]["start"][first] <= self.deadNotifiers[message["dead"]]["end"][first-1]+1:
              self.deadNotifiers[message["dead"]]["start"].pop(first)
              self.deadNotifiers[message["dead"]]["end"].pop(first-1)
          else:
            if ((self.deadNotifiers[message["dead"]]["start"][first] == message["start"] and
                 self.deadNotifiers[message["dead"]]["end"][first] >= message["end"]) or
                (first > 0 and
                 self.deadNotifiers[message["dead"]]["end"][first-1] >= message["end"])):
              message["dead"].sendMessage({"msg":"guilty","sender":self,"payments":0,"start":message["start"],"end":message["end"]})
              continue
            else:
              last = bisect.bisect_left(self.deadNotifiers[message["dead"]]["end"],message["end"])
              self.deadNotifiers[message["dead"]]["start"].insert(first,message["start"])
              self.deadNotifiers[message["dead"]]["end"].insert(last,message["end"])
              if first > 0:
                first = first - 1
              if last < len(self.deadNotifiers[message["dead"]]["end"])-1:
                last = last + 1
              while first < last:
                if self.deadNotifiers[message["dead"]]["start"][first+1] <= self.deadNotifiers[message["dead"]]["end"][first]+1:
                  self.deadNotifiers[message["dead"]]["start"].pop(first+1)
                  self.deadNotifiers[message["dead"]]["end"].pop(first)
                  last = last - 1
                else:
                  first = first+1
        if bIsAlive:
          payments = 0
        else:
          payments = self.handleDiedWhenDead(message)
        message["dead"].sendMessage({"msg":"guilty","sender":self,"payments":payments,"start":message["start"],"end":message["end"]})
      if bIsAlive:
        if message["dead"].getID() in self.ledger[-1][NEIGHBOURS]:
          if bGrowLedger:
            self.growLedger()
            bGrowLedger = False
          self.ledger[-1][NEIGHBOURS].pop(message["dead"].getID(),None)
    self.diedMessages = []

  def acceptPayment(self, amount, start, end):
    stop = start
    fine = amount / (end+1-start)
    while stop<end+1:
      index = bisect.bisect_right(self.ledgerIndex, start)-1
      stop = min(self.ledger[index][END],end)+1
      if stop <= start:
        print("!!!!!!!!!              indeed I broke             !!!!!!!!!!!!!!")
        import pdb; pdb.set_trace()
        break
      self.ledger[index][FINE] = self.ledger[index][FINE] + fine*(stop-start)
      print(self,fine*(stop-start),sep=',',end=',')
      start = stop

  def doKill(self):
    print(self,
          "started:", self.ledger[0][START],
          "minted:",sum([record[MINTED] for record in self.ledger]),
          "fined:",sum([record[FINE] for record in self.ledger]),
          "paid:",sum([record[PAID] for record in self.ledger]))
#    for record in self.ledger:
#      print(" ",record)
    super().doKill()


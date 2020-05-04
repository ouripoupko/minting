
import identity
import honest
import random

class Sybil(identity.Identity):

  def __init__(self,settings,myid,everyone,loop):
    identity.Identity.__init__(self,settings,myid,everyone,loop)

  def isAFriend(self, identity):
    if isinstance(identity,honest.Honest):
      return False
    return True

  def age(self):
    if random.random() < self.settings.exposeProbability:
      # calculate fine
      payments = 0
      for record in self.ledger:
        fine = (record[identity.MINTED]*2 + record[identity.FINE])/len(record[identity.NEIGHBOURS])
      # inform neighbours
        for neighbour in record[identity.NEIGHBOURS].values():
          payments = payments + 1
          neighbour.sendMessage({"msg":"died",
                                 "sender":self,
                                 "visited":[self],
                                 "start":record[identity.START],
                                 "end":record[identity.END],
                                 "fine":fine})
      # inform community
      self.everyone.sendMessage({"msg":"died", "sender":self, "payments":payments})
      # die
      return False
    return True

  def handleDiedWhenDead(self,index,message,fine,stop,start):
    neighbours = set(self.ledger[index][identity.NEIGHBOURS].values()).difference(message["visited"])
    if len(neighbours) == 0:
      import pdb; pdb.set_trace()
    passFine = fine*(stop-start)/len(neighbours)
    payments = 0
    for neighbour in neighbours:
      payments = payments + 1
      neighbour.sendMessage({"msg":"died",
                             "sender":self,
                             "visited":message["visited"]+[self],
                             "start":start,
                             "end":stop-1,
                             "fine":passFine})
    return payments

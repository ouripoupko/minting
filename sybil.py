
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
      for record in self.ledger:
        fine = record[identity.MINTED]*2 + record[identity.FINE]
      # inform neighbours
        print(self,[ident.getID() for ident in record[identity.NEIGHBOURS].values()])
        for neighbour in record[identity.NEIGHBOURS].values():
          neighbour.sendMessage({"msg":"exposed",
                                 "sender":self,
                                 "visited":[self],
                                 "start":record[identity.START],
                                 "end":record[identity.END],
                                 "fine":fine})
      # inform community
      self.everyone.sendMessage({"msg":"exposed", "sender":self})
      print(self,"died",fine)
      # die
      self.state = identity.DEAD

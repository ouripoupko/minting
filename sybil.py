
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
        print(self,"loop",self.loop,"minted",record[identity.MINTED],"from",record[identity.START],"to",record[identity.END],"with neighbours",record[identity.NEIGHBOURS])
      # inform neighbours
        for neighbour in record[identity.NEIGHBOURS].values():
          payments = payments + 1
          neighbour.sendMessage({"msg":"exposed",
                                 "sender":self,
                                 "visited":[self],
                                 "start":record[identity.START],
                                 "end":record[identity.END],
                                 "fine":fine})
      # inform community
      self.everyone.sendMessage({"msg":"exposed", "sender":self, "payments":payments})
      print(self,"died")
      # die
      return False
    return True


import identity
import random

class Genuine(identity.Identity):

  def __init__(self,settings,myid,everyone,loop):
    identity.Identity.__init__(self,settings,myid,everyone,loop)

  def age(self):
    if random.random() < self.settings.deathProbability:
      # inform neighbours
      for neighbour in self.ledger[-1][identity.NEIGHBOURS].values():
        neighbour.sendMessage({"msg":"died", "sender":self, "dead":self})
      # inform community
      self.everyone.sendMessage({"msg":"died", "sender":self})
#      print(self,"died")
      # die
      return False
    return True
    
  def handleDiedWhenDead(self,message):
    return 0


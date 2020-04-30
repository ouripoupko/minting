
import identity
import random

class Genuine(identity.Identity):

  def __init__(self,settings,myid,everyone,loop):
    identity.Identity.__init__(self,settings,myid,everyone,loop)

  def age(self):
    if random.random() < self.settings.deathProbability:
      # inform neighbours
      for neighbour in self.ledger[-1][identity.NEIGHBOURS].values():
        neighbour.sendMessage({"msg":"died",
                               "sender":self})
      # inform community
      self.everyone.sendMessage({"msg":"died", "sender":self})
#      print(self,"died")
      # die
      return False
    return True
    
  def handleDiedWhenDead(self,index,message,fine,stop,start):
    self.ledger[index][identity.FINE] = self.ledger[index][identity.FINE] + fine*(stop-start)
#    print(self,"loop",self.loop,"accept fine",fine*(stop-start),"from",self.ledger[index][identity.START],"to",self.ledger[index][identity.END])
    return 0



from identity import Identity
import honest
import random

class Sybil(Identity):

  def __init__(self,settings,myid,everyone):
    Identity.__init__(self,settings,myid,everyone)

  def isAFriend(self, identity):
    if isinstance(identity,honest.Honest):
      return False
    return True

  def age(self)
    if random.random() < self.settings.exposeProbability:
      

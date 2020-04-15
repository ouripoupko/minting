
from identity import Identity
import sybil

class Honest(Identity):

  def __init__(self,settings,myid,everyone,loop):
    Identity.__init__(self,settings,myid,everyone,loop)

  def isAFriend(self, identity):
    if isinstance(identity,sybil.Sybil):
      return False
    return True


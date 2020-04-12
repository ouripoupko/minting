
from identity import Identity
import sybil

class Honest(Identity):

  def __init__(self,settings,myid,everyone):
    Identity.__init__(self,settings,myid,everyone)

  def isAFriend(self, identity):
    if isinstance(identity,sybil.Sybil):
      return False
    return True


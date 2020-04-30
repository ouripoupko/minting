
import genuine
import sybil

class Honest(genuine.Genuine):

  def __init__(self,settings,myid,everyone,loop):
    genuine.Genuine.__init__(self,settings,myid,everyone,loop)

  def isAFriend(self, identity):
    if isinstance(identity,sybil.Sybil):
      return False
    return True



from identity import Identity

class Corrupt(Identity):

  def __init__(self,settings,myid,everyone,loop):
    Identity.__init__(self,settings,myid,everyone,loop)

  def isAFriend(self, identity):
    return True


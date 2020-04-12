
from identity import Identity

class Corrupt(Identity):

  def __init__(self,settings,myid,everyone):
    Identity.__init__(self,settings,myid,everyone)

  def isAFriend(self, identity):
    return True


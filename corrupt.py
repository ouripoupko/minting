
import genuine
import random

class Corrupt(genuine.Genuine):

  def __init__(self,settings,myid,everyone,loop):
    genuine.Genuine.__init__(self,settings,myid,everyone,loop)

  def isAFriend(self, identity):
    return True



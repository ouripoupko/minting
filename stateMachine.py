

from threadedQueue import ThreadedQueue

class State:

  def __init__(self,sm,message = None):
    self.sm = sm
    self.message = message

  def __str__(self):
    return str(self.sm) + ":" + type(self).__name__

  def next(self, message):
    return [self,None]

  def actionOnEntry(self):
    return [None,None]

  def actionOnExit(self):
    pass

class StateMachine(ThreadedQueue):

  def __init__(self):
    ThreadedQueue.__init__(self)
    self.state = None

  def handleMessage(self, message):
#    if self.getID()>0:
#      print(self.state,message)
    [next, transition] = self.state.next(message)
    while next:
      self.state.actionOnExit()
      if transition:
        transition()
      self.state = next
      [next, transition] = self.state.actionOnEntry()

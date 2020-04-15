

from threadedQueue import ThreadedQueue

class State:

  def __init__(self,sm,message = None):
    self.sm = sm
    self.message = message

  def __str__(self):
    return str(self.sm) + ":" + type(self).__name__

  def next(self, message):
    print(self,"next message")
    return [self,None]

  def actionOnEntry(self):
    print(self, "actionOnEntry")
    return [None,None]

  def actionOnExit(self):
    print(self, "actionOnExit")


class Condition:

  def __init__(self,sm,message = None):
    self.sm = sm
    self.message = message

  def resolve(self):
    return State(self.sm)


class StateMachine(ThreadedQueue):

  def __init__(self):
    ThreadedQueue.__init__(self)
    self.state = None

  def handleMessage(self, message):
    [next, transition] = self.state.next(message)
    while next:
      self.state.actionOnExit()
      if transition:
        transition()
      if isinstance(next,Condition):
        next = next.resolve()
      self.state = next
      [next, transition] = self.state.actionOnEntry()

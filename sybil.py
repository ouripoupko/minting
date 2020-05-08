
import identity
import honest
import random
import bisect

class Sybil(identity.Identity):

  def __init__(self,settings,myid,everyone,loop):
    identity.Identity.__init__(self,settings,myid,everyone,loop)

  def isAFriend(self, identity):
    if isinstance(identity,honest.Honest):
      return False
    return True

  def age(self):
    if random.random() < self.settings.exposeProbability:
      # calculate fine
      self.apocalypse = {"payments":0,"records":[]}
      for record in self.ledger:
        self.apocalypse["records"].append({"fine":record[identity.MINTED]*2 + record[identity.FINE],"start":record[identity.START],"end":record[identity.END],"found":set()})
        # inform neighbours
        for neighbour in record[identity.NEIGHBOURS].values():
          self.apocalypse["payments"] = self.apocalypse["payments"]+1
          neighbour.sendMessage({"msg":"died",
                                 "sender":self,
                                 "dead":self,
                                 "start":record[identity.START],
                                 "end":record[identity.END]})
          print(neighbour)
      print(self.apocalypse)
      # die
      return False
    return True


  def CollectReplies(self,message):
    self.apocalypse["payments"] = self.apocalypse["payments"] + message["payments"] - 1
    if message["payments"] == 0:
      starts = [rec["start"] for rec in self.apocalypse["records"]]
      first = bisect.bisect_left(starts,message["start"])
      if starts[first] > message["start"]:
        record = self.apocalypse["records"][first-1]
        fine = record["fine"]*(record["end"]+1-message["start"])/(record["end"]+1-record["start"])
        self.apocalypse["records"].insert(first,{"fine":fine,"start":message["start"],"end":record["end"],"found":record["found"].copy()})
        record["fine"] = record["fine"]-fine
        record["end"] = message["start"]-1
      ends = [rec["end"] for rec in self.apocalypse["records"]]
      last = bisect.bisect_left(ends,message["end"])
      if ends[last] > message["end"]:
        record = self.apocalypse["records"][last]
        fine = record["fine"]*(message["end"]+1-record["start"])/(record["end"]+1-record["start"])
        self.apocalypse["records"].insert(last,{"fine":fine,"start":record["start"],"end":message["end"],"found":record["found"].copy()})
        record["fine"] = record["fine"]-fine
        record["start"] = message["end"]-1
      for index in range(first,last+1):
        self.apocalypse["records"][index]["found"].add(message["sender"])
    # inform everyone their fine
    criminals = set()
    if self.apocalypse["payments"] == 0:
      for record in self.apocalypse["records"]:
        payment = record["fine"]/len(record["found"])
        for neighbour in record["found"]:
          neighbour.sendMessage({"msg":"pay","amount":payment,"start":record["start"],"end":record["end"]})
          criminals.add(neighbour)
      for criminal in criminals:
        criminal.sendMessage({"msg":"done","sender":self})
      # inform community
      self.everyone.sendMessage({"msg":"died", "sender":self})
    print(message)
    print(self.apocalypse)


  def handleDiedWhenDead(self,message):
    start = message["start"]
    end = message["end"]
    stop = start
    payments = 0
    while stop<end+1:
      index = bisect.bisect_right(self.ledgerIndex, start)-1
      stop = min(self.ledger[index][identity.END],end)+1
      if stop <= start:
        break
      start = stop
      neighbours = set(self.ledger[index][identity.NEIGHBOURS].values()).difference([message["sender"],message["dead"]])
      if not neighbours:
        print("!!!!!!!          I am a dead sybil, and got no corrupt neighbour        !!!!!!")
        import pdb; pdb.set_trace()
      for neighbour in neighbours:
        payments = payments + 1
        neighbour.sendMessage({"msg":"died",
                               "sender":self,
                               "dead":message["dead"],
                               "start":start,
                               "end":stop-1})
    return payments

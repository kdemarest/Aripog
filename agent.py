from history import History

class Agent:
	def __init__(self, name, target):
		self.name = name
		self.target = target
		self.history = History()
		self.history.add("system", "You are a pragmatic, rational person.")
	def setTarget(self,target):
		self.target = target

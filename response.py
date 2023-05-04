
class Response:
	def __init__(self):
		self.agent = None
		self.world = None
		self.message = None
		self.policy = None
		self.isError = False

	@classmethod
	def error(cls, message):
		self = cls()
		self.agent = "System"
		self.message = "ERROR: "+message
		self.isError = True
		return self

	@classmethod
	def notify(cls, message):
		self = cls()
		self.agent = "System"
		self.message = message
		return self

	@classmethod
	def standard(cls, agent: str, message: str, world: str = None, policy: str = None):
		self = cls()
		self.agent = agent
		self.message = message
		self.world = world
		self.policy = policy
		return self

	def toDict(self):
		return {
			"agent": self.agent,
			"message": self.message,
			"policy": self.policy,
			"isError": self.isError
		}


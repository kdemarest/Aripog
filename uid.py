class UidGenerator:
	def __init__(self, start=1000):
		self.next_id = start

	def notifyOfUid(self,uid):
		if uid >= self.next_id:
			self.next_id = uid + 1

	def generateUid(self):
		uid = str(self.next_id)
		self.next_id += 1
		return uid

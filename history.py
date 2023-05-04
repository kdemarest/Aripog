from typing import List, Dict

class History:
	def __init__(self) -> None:
		self.list: List[Dict[str, str]] = []

	@classmethod
	def single(cls, message):
		self = cls()
		self.add("user", message)
		return self

	def add(self, role: str, content: str) -> None:
		self.list.append(
			{
			'role': role,
			# 'name': the optional username
			'content': content
			}
		)

	def clear(self) -> None:
		self.list = []

	def getList(self) -> List[Dict[str, str]]:
		return self.list

	def getAsString(self) -> str:
		s: str = ""
		for entry in self.list:
			if s!="": 
				s += " "
			s += entry["content"]
		return s
	
export = History
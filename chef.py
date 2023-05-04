from log import log
from yak import yak_parse

class Chef:
	_instance = None
	def __new__(cls):
		if not cls._instance:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		self.world = None
		self.hintList: dict = {}
		self.recipeList: dict = {}

	def configure(self, world):
		self.world = world
		self.world.chef = self

	def recipeExists(self, recipeId: str):
		return recipeId in self.recipeList

	def hintExists(self, hintId: str):
		return hintId in self.hintList

	def getPrompt(self, recipeId: str) -> str:
		return self.recipeList[recipeId]['prompt']

	def getHint(self, hintId: str) -> str:
		return self.hintList[hintId]

	def parseHints(self, hintTextCombined):
		hintTextList = ("\n"+hintTextCombined).split("\n!")
		for hintText in hintTextList:
			lines = hintText.split("\n", 1)
			if len(lines)<=0: continue
			varList = yak_parse("identity="+lines[0])
		varList['body'] = "" if len(lines)<2 else lines[1]
		self.hintList[varList['identity']] = varList

	def parseRecipes(self, recipeTextCombined: str):
		recipeTextList = ("\n"+recipeTextCombined).split("\n!")
		log.debug("Recipe Count="+str(len(recipeTextList)))
		for recipeText in recipeTextList:
			lines = recipeText.split("\n", 1)
			if len(lines)<2: continue
			varList = yak_parse("recipeId="+lines[0])
			varList['prompt'] = "" if len(lines)<2 else lines[1]
			log.debug("Recipe "+varList['recipeId'])
			self.recipeList[varList['recipeId']] = varList

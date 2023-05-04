import os
import json
from uid import UidGenerator

class World:
	_instance = None
	def __new__(cls):
		if not cls._instance:
			cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		self.chef = None
		self.uidGen = UidGenerator()
		self.substrate = {}
		self.worldFile = "world.json"

	@property
	def entityList(self, index:str):
		return self.substrate[index]

	def configure(self,chef):
		self.chef = chef

	def addEntity(self, type: str, source: dict):
		uid = self.uidGen.generateUid()
		entity = {
			'type': type,
			'uid': uid,
			'keywords': source.get('keywords',{})
		}
		for key in source:
			entity[key] = source[key]
		self.substrate[uid] = entity
		return entity

	def save(self):
		with open(self.worldFile, 'w') as f:
			json.dump( self.substrate, f, indent=4)

	def load(self):
		if not os.path.exists(self.worldFile):
			return
		with open(self.worldFile, 'r') as f:
			json.load(self.substrate, f)
		for entity in self.entityList:
			assert all(key in entity for key in {'type','uid'}), "Entity missing required keys."
			self.uidGen.notifyOfUid(entity['uid'])

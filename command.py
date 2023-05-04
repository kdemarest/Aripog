import inspect
from log import log
import re
import shlex

class Commander:
	def __init__(self):
		self.commands = {}

	def register(self, command, callback):
		self.commands[command] = callback

	def parse(self, commandString):
		parameters = shlex.split(commandString)
		if len(parameters)==0:
			return "", []
		command = parameters.pop(0)
		return command, parameters

	def commandExists(self, command: str):
		return command in self.commands

	def execute(self, command, params):
		fn = self.commands[command]
		#if inspect.iscoroutinefunction(fn):
		#	return await fn(params)
		return fn(params)

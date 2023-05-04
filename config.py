import json

def read(configFileName):
	with open(configFileName) as file:
		jsonData = json.load(file)
	return jsonData

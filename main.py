#
# watchmedo shell-command -p '*.py' --recursive --wait --command='python3 main.py' .
#

from typing import List
import os
import config
from log import log
import json
from flask import jsonify
from agent import Agent
from server import server, Response
from gpt import Gpt
from chef import Chef
from world import World
from command import Commander
from gpt import Gpt
from history import History
from tokenizer import tokenReplace

serverConfig = config.read('configServer.json')

api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
	raise Exception("Error: OPENAI_API_KEY environment variable not set")

user = Agent("User", None)
maker = Agent("Maker", user)
fred = Agent("Fred", user)
user.setTarget(fred)

def getToken(token, context = {}):
	keys_list = token.split('.')

	def search(val):
		for key in keys_list:
			if not isinstance(val,dict):
				typeName = type(val).__name__
				log.debug(f"key {key} is {typeName} in {token}")
				return None
			val = val.get(key)
			if not val:
				return None
		return val

	result = search(context)
	if result!=None: return result
	result = search(chef.hintList)
	if result!=None: return result
	result = search(chef.recipeList)
	if result!=None: return result
	result = search(world.substrate)
	return result or '{'+token+'}'

def cmdReset(params) -> Response:
	user.target.history.clear()
	return Response.notify("History reset.")

def cmdBlab(params) -> Response:
	return Response.notify("The quick brown fox jumped over the lazy dog. She sells sea shells by the sea shore. Peter piper picked a peck of pickled peppers. How many peppers did Peter Piper pick?")

def cmdJson(params) -> Response:
	return Response.notify(
		'''
		{"Region": {"Name": "Methane Mire", "Summary": "swamp", "Sentients": [{"Name": "Croakfolk", "Description": "Frog-like humanoids that inhabit the swamp regions. They are skilled in swimming and use their long tongues to catch prey."}, {"Name": "Moon Elves", "Description": "An ancient race of elves that once inhabited the region but have long since disappeared. Their ruins can still be found sunken in the swamp."}], "Ruins": ["Sunken Moon Elf ruins", "Decaying Croakfolk huts"], "Resources": ["Methane gas", "Swamp plants", "Fish", "Crustaceans", "Reeds", "Clay", "Coal", "Iron", "Gems", "Rare metals"], "Hazards": ["Flooded tunnels", "Deep mud", "Toxic gases", "Sharp roots", "Sudden drops", "Croakfolk attacks", "Giant leeches", "Teethy fish", "Rotting logs"], "Creatures": ["Giant snapping turtles", "Electric eels", "Poison dart frogs", "Giant dragonflies", "Swamp rats", "Fishing spiders", "Cave bats", "Moldy cave bears", "Glimmering fireflies"]}, "entityType": "Region", "uid": "0", "keywords": {}}
		Made Region and added it to world
		'''
	)

def jsonToPythonData(jsonString):
	firstBrace = jsonString.find('{')
	lastBrace = jsonString.rfind('}')
	return json.loads(jsonString[firstBrace:lastBrace+1])

def cmdShow(params) -> Response:
	token = params[0]
	if not token:
		return Response.error("No parameter specified.")
	
	text = getToken(token)
	return Response.standard(
		agent="Maker",
		message=text
	)

# Make an entity in the world.
def cmdMake(params) -> Response:
	recipeId = params[0]
	if not recipeId or not chef.recipeExists(recipeId):
		return Response.error(f"No recipe {recipeId}");
	context = {}
	if len(params)>=2 and chef.hintExists(params[1]):
		context['context'] = chef.getHint(params[1])
	promptRaw = "{Preface}\n"+chef.getPrompt(recipeId)
	prompt = tokenReplace(promptRaw, lambda token: getToken(token, context))

	response = gpt.chat(History.single(prompt))
	if response.isError:
		return response

	entitySource = jsonToPythonData(response.message)
	topKey = next(iter(entitySource))
	entity = world.addEntity(recipeId, entitySource[topKey])

	entityJson = "<pre>"+json.dumps(entity, indent=4)+"</pre>"

	# for each 'need' check whether 

	return Response.standard(
		agent="Maker",
		world=entityJson,
		message=f"Made {entity['entityType']} and added it to world"
	)

def cmdSave(params) -> Response:
	world.save()
	return Response.notify("World Saved.")

commander = Commander()
commander.register("/error", lambda params: Response.error("Unknown command"))
commander.register("/ping", lambda params: Response.notify("pong"))
commander.register("/reset", cmdReset)
commander.register("/blab", cmdBlab)
commander.register("/json", cmdJson)
commander.register("/show", cmdShow)
commander.register("/make", cmdMake)
commander.register("/save", cmdSave)


def onUserCommand(commandString: str):
	(command,parameters) = commander.parse(commandString)
	if not commander.commandExists(command):
		return Response.error(f"Unknown command {command}")
	return commander.execute(command,parameters)

def onUserChat(message: str):
	recipient = user.target
	recipient.history.add("user",message)
	response = gpt.chat(recipient.history)
	if not response.isError:
		recipient.history.add("assistant", response.message)
		response.agent = recipient.name
	return response

world = World()
chef = Chef()
world.configure(chef=chef)
chef.configure(world=world)

with open('hints.yak', 'r') as f:
	chef.parseHints(f.read())

with open("recipes.yak", "r") as f:
	chef.parseRecipes(f.read())

world.worldFile = "world.json"
world.load()

gpt = Gpt(model=serverConfig["gptModel"])
serverConfig["gptModel"]

server.onUserChat = onUserChat
server.onUserCommand = onUserCommand
server.run(host='0.0.0.0', port=serverConfig['port'])

'''
Travel
- you travel indoors by going through doors.
- you travel in wilderness by going to landmarks.

Location
- room in a building in a settlement in a region
- room in a dungeon in a locale in a region
- room in a 
- (room, locale)
  in a (settlement, ruin, dungeon, wilderness)

  
Swamp Places: nook, cove, inley, bayou, bog, slough



ok, the next step is this:
Write hand-made code to decide how it should work. Get to the point
of creating a person and talking with them.


IT WOULD BE NICE IF:

/edit puts you into edit mode, editing the thing you last edited.

left panel = list of every prompt by name
right panel = the latest prompt you were editing
- the right panel is just a text box. For any prompt you can define 
-- name - the unique name of the prompt, like Creature or Region
-- query - a list of keywords to search when fetching context data for this prompt
-- seeds - a list of explicit seeds that springboard from this element, 
   like a Region or two for a World, or five SentientRaces for the world.
-- extract - a list of types you should expect this prompt to make, like Items, Creatures, etc.
-- body - the text of the prompt itself

/prep (or Ctrl+Enter) runs the query and lets you preview the resulting final prompt
/make (or Alt+Enter) does the prep and submits it to ChatGPT for completion

/summary - emits a summary list of all made elements in a list: |type|count|
/list <type> <criteria> shows all elements of type that meet criteria

/tocode - ask chatgpt to convert the fields this thing created into python fields

'''

'''
Sample error response
message='OpenAI API response'
path=https://api.openai.com/v1/chat/completions
processing_ms=160
request_id=3f1987d522d55017909784d4c24a0561
response_code=400
error_code=context_length_exceeded
error_message="This model's maximum context length is 4097 tokens. However, you requested 4109 tokens (22 in the messages, 4087 in the completion). Please reduce the length of the messages or completion." error_param=messages
error_type=invalid_request_error message='OpenAI API error received'
stream_error=False

Agli
Coach - knows what to ask boss.
Boss - responds to guide, then acts

Coach:
'm working on a way to ask AI to accomplish things. I will provide an objective, and then the AI needs to start framing up what it is going to do. What is the first question I should be asking?



'''
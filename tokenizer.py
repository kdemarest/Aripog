import json

# Returns a JSON string with token as the key, and the contents of tokenDict
def tokenToJsonString(tokenDict: dict, token: str) -> str:
	dictWithNesting = { token: tokenDict[token] }
	jsonString = json.dumps(dictWithNesting, indent=2)
	return jsonString

# Replaces all {tokens} found in str by calling lookupTokenFn
def tokenReplace(sourceString: str, lookupTokenFn):
	start = 0
	result = ""

	while start < len(sourceString):
		# Look for opening and closing braces
		pos1 = sourceString.find("{", start)
		if pos1 == -1:
			result += sourceString[start:]
			break

		pos2 = sourceString.find("}", pos1)
		if pos2 == -1:
			result += sourceString[start:]
			break

		# Append the part before the token
		result += sourceString[start:pos1]

		# Get the token string
		tokenString = sourceString[pos1+1:pos2]

		# Lookup the token and append the value
		tokenValue = lookupTokenFn(tokenString)
		result += tokenValue

		# Update the starting position
		start = pos2+1

	return result
	
def test_tokenToJsonString():
	# Test case 1: Normal dictionary
	tokenDict = {"fruit": "apple"}
	token = "fruit"
	expected = '{"fruit": "apple"}'
	output = tokenToJsonString(tokenDict, token)
	assert output == expected
	
	# Test case 2: None value in dictionary
	tokenDict = {"fruit": None}
	token = "fruit"
	expected = '{"fruit": null}'
	output = tokenToJsonString(tokenDict, token)
	assert output == expected
	
	# Test case 3: Nested dictionary
	tokenDict = {"fruit": {"apple": 1, "banana": 2}}
	token = "fruit"
	expected = '{"fruit": {"apple": 1, "banana": 2}}'
	output = tokenToJsonString(tokenDict, token)
	assert output == expected

	
def test_tokenReplace():
	lookupTokenFn = lambda x: x.upper()
	sourceString = "Hello, {name}! You have {count} new messages."
	expected = "Hello, JANE! You have 3 NEW MESSAGES."
	output = tokenReplace(sourceString, lookupTokenFn)
	assert output == expected

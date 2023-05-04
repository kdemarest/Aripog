def yak_parse(kvString:str)->dict:
	result = {}
	inString = False
	found = ''
	key = None
	for i in range(len(kvString)):
		s = kvString[i]
		if s=='=':
			found = found.strip()
			parts = found.rsplit(" ", 1)
			nextKey = parts.pop().strip()
			if key:
				result[key] = parts.pop().strip()
			key = nextKey
			found = ''
			continue
		found += s
	if key:
		result[key] = found.strip()
	return result

def test_yak_parse():
	# Test with one key-value pair
	input_str = "key=value"
	expected_output = {"key": "value"}
	assert yak_parse(input_str) == expected_output
	
	# Test with multiple key-value pairs
	input_str = "key1=value1 key2=value2"
	expected_output = {"key1": "value1", "key2": "value2"}
	assert yak_parse(input_str) == expected_output
	
	# Test with no key-value pairs
	input_str = ""
	expected_output = {}
	assert yak_parse(input_str) == expected_output
	
	# Test with leading/trailing spaces
	input_str = "  key\t=   \tvalue  "
	expected_output = {"key": "value"}
	assert yak_parse(input_str) == expected_output
	
	# Test with key-value pairs with spaces
	input_str = "key1=value1 key2=value2a, value2b key3 =  val u e 3  "
	expected_output = {"key1": "value1", "key2": "value2a, value2b", "key3": "val u e 3"}
	assert yak_parse(input_str) == expected_output


if __name__=='__main__':
	test_yak_parse()

import openai
import tiktoken
from server import Response
from history import History

class Usage:
	def __init__(self):
		self.promptTokens = 0
		self.completionTokens = 0
		self.totalTokens = 0

class Gpt:
	def __init__(self, model):
		self.usage = Usage()
		self.model = model

	def countTokens(self, messages, model):
		"""Returns the number of tokens used by a list of messages."""
		try:
			encoding = tiktoken.encoding_for_model(model)
		except KeyError:
			print("Warning: model not found. Using cl100k_base encoding.")
			encoding = tiktoken.get_encoding("cl100k_base")
		if model == "gpt-3.5-turbo":
			print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
			return self.countTokens(messages, model="gpt-3.5-turbo-0301")
		elif model == "gpt-4":
			print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
			return self.countTokens(messages, model="gpt-4-0314")
		elif model == "gpt-3.5-turbo-0301":
			tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
			tokens_per_name = -1  # if there's a name, the role is omitted
		elif model == "gpt-4-0314":
			tokens_per_message = 3
			tokens_per_name = 1
		else:
			raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
		num_tokens = 0
		for message in messages:
			num_tokens += tokens_per_message
			for key, value in message.items():
				num_tokens += len(encoding.encode(value))
				if key == "name":
					num_tokens += tokens_per_name
		num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
		return num_tokens

	def chat(self, history: History) -> Response:

		maxTokens = 4096 - self.countTokens(history.getList(), self.model)

		reps = 5
		text = ""
		finish = None
		while reps > 0 and finish==None and len(text) < 8000:
			reps -= 1
			try:
				# Docs: https://platform.openai.com/docs/api-reference/chat/create
				result = openai.ChatCompletion.create(
					model = self.model,
					messages = history.getList(),
					max_tokens = maxTokens
					# temperature=1
					# top_p = 1
					# n = number of choices (1)
					# stream = whether to stream partial results (false)
					# presence_penalty
					# frequency_penalty
				)
			except Exception as e:
				return Response.error("Calling API "+str(e))
			
			try:
				if result.choices[0].message.content!="":
					if not result.choices[0].finish_reason in [None, "stop", "length", "content_filter"]:
						raise Exception("Unexpected finish_reason "+result.choices[0].finish_reason)
				self.usage.promptTokens += result.usage.prompt_tokens
				self.usage.completionTokens += result.usage.completion_tokens
				finish = result.choices[0].finish_reason
				text += result.choices[0].message.content
			except Exception as e:
				return Response.error("Chat response malformed "+str(e))
			if finish==None:
				finish="None..."

		return Response.standard(
			agent=None,
			message=text, 
			policy="filtered" if finish == "content_filter" else None
		)

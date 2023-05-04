import os
from log import log
from flask import Flask, send_from_directory, request, jsonify, send_file
from response import Response

server = Flask(__name__, static_url_path='', static_folder='static')

@server.route("/")
def serve_index():
	return send_from_directory(os.path.join(server.root_path, 'static'), 'index.html')

@server.route('/<path:filename>')
def serve_files(filename):
	return send_from_directory(server.static_folder, filename)

@server.route('/chat', methods=['POST'])
async def chat():
	message = request.json['message']

	if(message[0]=="/"):
		response: Response = server.onUserCommand(message)
		return jsonify(response.toDict())

	response: Response = server.onUserChat(message)
	return jsonify(response.toDict())

from flask import jsonify
from constants import whitelisted_extensions, error_codes

import os

def send_error(error_code, message):
	return jsonify({ 'error' : {
						'code' : error_code,
						'message' : message
					}
				})

def send_state_message(track, message, extra = None, response_code = error_codes.SUCCESFULL_QUERY):

	response = { 'code' : response_code,
				'message' : message,
				'title' : track.getMetadata().get('metadata').get('title'),
				'path' : track.getPath(),
				'state' : {'playing' : track.isPlaying(), 'paused' : track.isPaused()}}

	if extra != None:
		response.update(extra)

	return jsonify(response)

def track_endevent(track):
	track.restart()

def is_valid_file(path):
	ext = os.path.splitext(path)[1]
	for extension in whitelisted_extensions:
		if extension == ext:
			return True
	return False

def check_boolean(request, field):
	if(request.method == 'POST'):
		return True if request.form.get(field, type = str) == 'true' or request.form.get(field, type = str) == 'True' else False
	else:
		return True if request.args.get(field) == 'true' or request.args.get(field) == 'True' else False
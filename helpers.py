from flask import jsonify
from constants import whitelisted_extensions, error_codes, defaults
from settings import volumizer
import os

def get_defaults(response_code = error_codes.SUCCESFULL_QUERY):
	response = {
		"defaults" : {
			"default_path" : defaults.path
		}
	}
	return response

def send_error(error_code, message, json = True):
	response = { 'error' : {
							'code' : error_code,
							'message' : message
						}
				}
	if json:
		return jsonify(response)
	else:
		return response

def send_state_track_message(track, message, extra = None, response_code = error_codes.SUCCESFULL_QUERY):

	response = { 'code' : response_code,
				'message' : message,
				'title' : track.getMetadata().get('metadata').get('title'),
				'path' : track.getPath(),
				'state' : {'playing' : track.isPlaying(), 'paused' : track.isPaused(), 'muted' : volumizer.isMuted()}}

	if extra != None:
		response.update(extra)

	return jsonify(response)

def send_state_playlist_message(playlist, message, extra = None, playing = None, paused = None, response_code = error_codes.SUCCESFULL_QUERY):
	
	if playing == None:
		isPlaying = playlist.isPlaying()
	else:
		isPlaying = playing

	if paused == None:
		isPaused = playlist.isPaused()
	else:
		isPaused = paused

	response = { 'code' : response_code,
				'message' : message,
				'position' : playlist.getPosition(),
				'elements' : playlist.getTracks(),
				'nextTrack' : playlist.nextTrackAvilable(),
				'previousTrack' : playlist.prevTrackAvilable(),
				'state' : {'playing' : isPlaying, 'paused' : isPaused, 'muted' : volumizer.isMuted()}}

	if extra != None:
		response.update(extra)

	return jsonify(response)

def send_playlist_play_error(indexes, message, code = error_codes.INVALID_TRACKS):

	response = {'code' : code,
				'message' : message,
				'wrong_positions' : indexes
				}

	return jsonify(response)

def track_endevent(track):
	track.restart()

def is_valid_file(path):
	ext = os.path.splitext(path)[1]
	for extension in whitelisted_extensions:
		if extension == ext:
			return True
	return False

def is_valid_num(minimum, maximum, num):
	if num >= minimum and num <= maximum:
		return True
	return False

def check_boolean(request, field):
	if(request.method == 'POST'):
		return True if request.form.get(field, type = str) == 'true' or request.form.get(field, type = str) == 'True' else False
	else:
		return True if request.args.get(field) == 'true' or request.args.get(field) == 'True' else False

def check_string(request, field):
	if(request.method == 'POST'):
		return request.form.get(field, type = str)
	else:
		return request.args.get(field)

def check_integer(request, field):
	if(request.method == 'POST'):
		data = request.form.get(field, type = int)
	else:
		data = request.args.get(field)

	try:
		data = int(data)
		return data
	except:
		return None


def check_float(request, field):
	if(request.method == 'POST'):
		data = request.form.get(field, type = float)
	else:
		data = request.args.get(field)

	try:
		data = float(data)
		return data
	except:
		return None

def check_string_array(request, field):
	if request.method == 'POST':
		return request.form.getlist(field)
	else:
		return request.args.getlist(field)

def isNull(object):
	if object == None:
		return True
	return False
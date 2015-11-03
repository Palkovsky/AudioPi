from flask import jsonify
from constants import whitelisted_extensions, error_codes, defaults, sorting_methods
from settings import volumizer
from pygame import mixer
import os

def get_defaults(response_code = error_codes.SUCCESFULL_QUERY):
	response = {
		"defaults" : {
			"default_path" : defaults.path
		}
	}
	return response

def send_error(error_code, message, json = True):
	response = {
					'code' : error_code,
					'message' : message
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
	
	if playlist != None:
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

	else:
		return send_error(error_codes.UNDEFINED, "An error occured(Null pointer exception)")

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

def check_int_array(request, field):
	if request.method == 'POST':
		data = request.form.getlist(field, type = int)
	else:
		data = request.args.getlist(field)

	data_copy = data
	int_array = []

	for integer in data_copy:
		try:
			i = int(integer)
			int_array.append(i)
		except:
			pass

	return int_array	

def isNull(object):
	if object == None:
		return True
	return False

def send_no_file_error(path):
	return jsonify({
		"code" : error_codes.FILE_NOT_EXSISTS,
		"message" : "File doesn't exsist",
		"path" : path
	})

def file_exsists(path):
	if path != None:
		return os.path.isfile(path)
	return False

def flush_stream():
	try:
		mixer.music.stop()
	except:
		pass

def translate_sorting_method(sortMethod, default = 0):
	if isinstance(sortMethod, int):
		if sortMethod < 0 or sortMethod >= len(sorting_methods):
			return default
		else:
			return sortMethod
	elif isinstance(sortMethod, str):
		for method in sorting_methods:
			if sortMethod == method["name"]:
				return method["value"]
	return default
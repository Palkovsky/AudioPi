from flask import jsonify

def send_error(error_code, message):
	return jsonify({ 'error' : {
						'code' : error_code,
						'message' : message
					}
				})

def send_state_message(track, message):
	return jsonify({ 'track' : track.getMetadata().get('title'),
				'state' : {'playing' : track.isPlaying(), 'paused' : track.isPaused(),'message' : message}})

def track_endevent(track):
	track.restart()
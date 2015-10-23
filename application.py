from flask import Flask
from flask import request
from flask import jsonify
from constants import error_codes 
from helpers import send_error, send_state_message, track_endevent, is_valid_file, check_boolean
from threader import TrackThreader

import os

app = Flask(__name__)

musicThreader = TrackThreader()


@app.route('/track/play', methods=['GET', 'POST'])
def play():
	currentTrack = musicThreader.currentTrack()

	trackPath = ""
	termiate = False
	if(request.method == 'POST'):
		trackPath = request.form.get('p', type = str)
	else:
		trackPath = request.args.get('p')

	terminate = check_boolean(request, 't')

	if(currentTrack == None):
		return startTrack(trackPath)
	else:

		if terminate:
			currentTrack.stop()
			musicThreader.setTrack(None)
			return startTrack(trackPath)

		return send_error(error_codes.TRACK_ALREADY_PLAYING, "Track already exsists")

@app.route('/track/rewind', methods=['GET', 'POST'])
def rewind():
	currentTrack = musicThreader.currentTrack()
	
	destPos = -1
	unpause = True

	if(request.method == 'POST'):
		destPos = request.form.get('pos', type = int)
	else:
		destPos = request.args.get('pos')

	try:
		destPos = int(destPos)
	except:
		return send_error(error_codes.WRONG_PLAYBACK_POSITION, "Wrong playback position")

	unpause = check_boolean(request, 'unpause')

	if currentTrack == None:
		return send_error(error_codes.NO_TRACK, "No track playing")
	elif destPos == -1:
		return send_error(error_codes.WRONG_PLAYBACK_POSITION, "No position specified")
	elif destPos < 0 or destPos > round(currentTrack.getLength() / 1000):
		return send_error(error_codes.WRONG_PLAYBACK_POSITION, "Wrong playback position. It should be specified with seconds")
	else:

		oldPos = currentTrack.playbackInfo().get('playback').get('position').get('secs')
		total = currentTrack.playbackInfo().get('playback').get('total').get('secs')
		currentTrack.setPlaybackPosition(destPos)

		if unpause and currentTrack.isPaused():
			currentTrack.unpause()

		return send_state_message(currentTrack, "Playback position succesfully changed", {
				'newPosition' : destPos,
				'oldPosition' : oldPos,
				'total' : total
			})

@app.route('/track/pause')
def pause():
	currentTrack = musicThreader.currentTrack()

	if(currentTrack == None):
		return send_error(error_codes.NO_TRACK, "No track playing")
	elif(currentTrack.isPaused()):
		return send_error(error_codes.TRACK_ALREADY_PAUSED, "Track is already paused")
	else:
		currentTrack.pause()
		return send_state_message(currentTrack, "Track paused")
		
@app.route('/track/unpause')
def unpause():
	currentTrack = musicThreader.currentTrack()

	if(currentTrack == None):
		return send_error(error_codes.NO_TRACK, "No track playing")
	elif( not currentTrack.isPaused()):
		return send_error(error_codes.TRACK_ALREADY_PLAYING, "Track is already playing")
	else:
		currentTrack.unpause()
		return send_state_message(currentTrack, "Track unpaused")

@app.route('/track/metadata', methods=['GET'])
def metadata():
	currentTrack = musicThreader.currentTrack()
	if(currentTrack != None):
		return jsonify(currentTrack.getMetadata())
	return send_error(error_codes.NO_TRACK, "No track playing")

@app.route('/track/playback', methods=['GET'])
def playback():
	currentTrack = musicThreader.currentTrack()
	if(currentTrack != None):
		return jsonify(currentTrack.playbackInfo())
	return send_error(error_codes.NO_TRACK, "No track playing")


@app.route('/stop')
def stop():
	currentTrack = musicThreader.currentTrack()
	if(currentTrack != None):
		currentTrack.stop()
		musicThreader.setTrack(None)
		return jsonify({'message' : "Track stopped"})
	else:
		return send_error(error_codes.NO_TRACK, "No track playing")

#Utility methods
def startTrack(trackPath):
	#musicThreader.registerOnEndCustomCallback(track_endevent)

	if(trackPath == "" or trackPath == None):
		return send_error(error_codes.NO_PATH_DEFINED, "No path parameter passed.")

	if not os.path.exists(trackPath):
		return send_error(error_codes.WRONG_PATH_SPECIFIED, "File doesn't exsist.")

	if not is_valid_file(trackPath):
		return send_error(error_codes.INVALID_TYPE, "Invalid filetype.")

	data = musicThreader.getThread(trackPath)
	currentThread = data.get('thread')
	currentTrack = data.get('track')
	currentThread.start()
	return send_state_message(currentTrack, "Track started")

if __name__ == '__main__':
    app.run(debug=True)
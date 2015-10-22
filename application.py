from flask import Flask
from flask import jsonify
from constants import error_codes 
from helpers import send_error, send_state_message, track_endevent
from threader import TrackThreader

app = Flask(__name__)

musicThreader = TrackThreader()

@app.route('/track/play', methods=['GET', 'POST'])
def play():
	currentTrack = musicThreader.currentTrack()
	if(currentTrack == None):
		#musicThreader.registerOnEndCustomCallback(track_endevent)
		data = musicThreader.getThread("tracks/track4.mp3")
		currentThread = data.get('thread')
		currentTrack = data.get('track')
		currentThread.start()
		return send_state_message(currentTrack, "Track started")
	else:
		return send_state_message(currentTrack, "Track already exsists")

@app.route('/stop')
def stop():
	currentTrack = musicThreader.currentTrack()
	if(currentTrack != None):
		currentTrack.stop()
		musicThreader.setTrack(None)
		return jsonify({'message' : "Track stopped"})
	else:
		return send_error(error_codes.NO_TRACK, "No track playing")

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

if __name__ == '__main__':
    app.run(debug=True)
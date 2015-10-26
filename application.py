from flask import Flask
from flask import request
from flask import jsonify
from constants import error_codes 
from helpers import send_error, send_state_track_message
from helpers import send_state_playlist_message, track_endevent, is_valid_file, is_valid_num
from helpers import check_boolean, check_string, check_integer, check_string_array, isNull
from threader import TrackThreader, PlaylistThreader

import os

app = Flask(__name__)

trackThreader = TrackThreader()
playlistThreader = PlaylistThreader()

@app.route('/track/play', methods=['GET', 'POST'])
def play_track():
	currentTrack = trackThreader.currentTrack()

	trackPath = check_string(request, 'p')
	terminate = check_boolean(request, 't')

	if(currentTrack == None):
		return startTrack(trackPath)
	else:

		if terminate:
			currentTrack.stop()
			trackThreader.setTrack(None)
			return startTrack(trackPath)

		return send_error(error_codes.TRACK_ALREADY_PLAYING, "Track already exsists")

@app.route('/track/rewind', methods=['GET', 'POST'])
def rewind_track():
	currentTrack = trackThreader.currentTrack()
	
	destPos = check_integer(request, 'pos')
	unpause = True

	if destPos == None:
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

		return send_state_track_message(currentTrack, "Playback position succesfully changed", {
				'newPosition' : destPos,
				'oldPosition' : oldPos,
				'total' : total
			})

@app.route('/track/pause')
def pause_track():
	currentTrack = trackThreader.currentTrack()

	if(currentTrack == None):
		return send_error(error_codes.NO_TRACK, "No track playing")
	elif(currentTrack.isPaused()):
		return send_error(error_codes.TRACK_ALREADY_PAUSED, "Track is already paused")
	else:
		currentTrack.pause()
		return send_state_track_message(currentTrack, "Track paused")
		
@app.route('/track/unpause')
def unpause_track():
	currentTrack = trackThreader.currentTrack()

	if(currentTrack == None):
		return send_error(error_codes.NO_TRACK, "No track playing")
	elif( not currentTrack.isPaused()):
		return send_error(error_codes.TRACK_ALREADY_PLAYING, "Track is already playing")
	else:
		currentTrack.unpause()
		return send_state_track_message(currentTrack, "Track unpaused")

@app.route('/track/metadata', methods=['GET'])
def metadata_track():
	currentTrack = trackThreader.currentTrack()
	if(currentTrack != None):
		return jsonify(currentTrack.getMetadata())
	return send_error(error_codes.NO_TRACK, "No track playing")

@app.route('/track/playback', methods=['GET'])
def playback_track():
	currentTrack = trackThreader.currentTrack()
	if(currentTrack != None):
		return jsonify(currentTrack.playbackInfo())
	return send_error(error_codes.NO_TRACK, "No track playing")

@app.route('/track/stop')
def stop_track():
	currentTrack = trackThreader.currentTrack()
	if(currentTrack != None):
		currentTrack.stop()
		trackThreader.setTrack(None)
		return jsonify({'message' : "Track stopped"})
	else:
		return send_error(error_codes.NO_TRACK, "No track playing")


# PLAYLIST SECTION

@app.route('/playlist/play', methods=['GET', 'POST'])
def play_playlist():
	currentPlaylist = playlistThreader.currentPlaylist()

	defaultPosition = check_integer(request, 'i')
	terminate = check_boolean(request, 't')
	tracks = check_string_array(request, "track")

	#http://localhost:5000/playlist/play?track=tracks/track5.mp3&track=tracks/track2.mp3&track=tracks/track5.mp3&i=0&t=True

	if currentPlaylist == None:
		return startPlaylist(tracks, defaultPosition)
	else:

		if terminate:
			currentPlaylist.stop()
			playlistThreader.setPlaylist(None)
			playlistThreader.reInit()
			return startPlaylist(tracks, defaultPosition)

		return send_error(error_codes.PLAYLIST_EXSIST, "Playlist already exsist")

@app.route('/playlist/next')
def playlist_next():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None:
		if currentPlaylist.nextTrackAvilable():
			currentPlaylist.nextTrack()
			return send_state_playlist_message(currentPlaylist, "Track succesfully changed")
		else:
			return send_error(error_codes.NO_NEXT_TRACK, "No next track avilable")
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")


@app.route('/playlist/prev')
def playlist_prev():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None:
		if currentPlaylist.prevTrackAvilable():
			currentPlaylist.previousTrack()
			return send_state_playlist_message(currentPlaylist, "Track succesfully changed")
		else:
			return send_error(error_codes.NO_PREV_TRACK, "No previous track avilable")
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")

@app.route('/playlist/pos', methods=['GET', 'POST'])
def playlist_pos():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None:
		index = check_integer(request, 'i')

		if index == None or not is_valid_num(0, len(currentPlaylist.tracks) - 1, index):
			return send_error(error_codes.INVALID_TRACK_INDEX, "Invalid track index")
		else:
			currentPlaylist.play(index)
			return send_state_playlist_message(currentPlaylist, "Track succesfully changed")
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")

@app.route('/playlist/playback')
def playlist_playback():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None:
		return jsonify(currentPlaylist.playbackInfo(error_codes.SUCCESFULL_QUERY))
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")

@app.route('/playlist/stop')
def stop_playlist():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None:
		currentPlaylist.stop()
		playlistThreader.setPlaylist(None)

		return jsonify({'message' : "Playlist stopped" })
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")

#Utility methods
def startTrack(trackPath):
	#trackThreader.registerOnEndCustomCallback(track_endevent)

	if(trackPath == "" or trackPath == None):
		return send_error(error_codes.NO_PATH_DEFINED, "No path parameter passed.")

	if not os.path.exists(trackPath):
		return send_error(error_codes.WRONG_PATH_SPECIFIED, "File doesn't exsist.")

	if not is_valid_file(trackPath):
		return send_error(error_codes.INVALID_TYPE, "Invalid filetype.")

	data = trackThreader.getThread(trackPath)
	currentThread = data.get('thread')
	currentTrack = data.get('track')
	currentThread.start()
	return send_state_track_message(currentTrack, "Track started")

def startPlaylist(tracks, defaultPosition = 0):		
		if defaultPosition != None and is_valid_num(0, len(tracks) - 1, defaultPosition):
			data = playlistThreader.getThread(tracks, defaultPosition)
		else:
			data = playlistThreader.getThread(tracks)

		currentPlaylist = data.get('playlist')

		playlistThreader.startThread()

		return send_state_playlist_message(currentPlaylist, "Playlist succesfully started", None, 1, False)

if __name__ == '__main__':
    app.run(debug=True)
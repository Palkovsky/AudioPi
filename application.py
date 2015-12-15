from flask import Flask
from flask import request
from flask import jsonify, send_from_directory
from werkzeug import secure_filename
from constants import error_codes, params
from helpers import send_error, send_state_track_message
from helpers import send_state_playlist_message, track_endevent, is_valid_file, is_valid_num
from helpers import check_boolean, check_string, check_integer, check_float, check_string_array, isNull
from helpers import check_int_array, translate_sorting_method, send_no_dir_error, allowed_file
from helpers import send_playlist_play_error, get_defaults, file_exsists, send_no_file_error, flush_stream
from threader import TrackThreader, PlaylistThreader
from settings import volumizer
from explore import Explorer
import os
import shutil

app = Flask(__name__)

trackThreader = TrackThreader()
playlistThreader = PlaylistThreader()
explorer = Explorer()

@app.route('/track/play', methods=['GET', 'POST'])
def play_track():
	currentTrack = trackThreader.currentTrack()

	trackPath = check_string(request, params.PATH)
	terminate = check_boolean(request, params.TERMINATE)

	if not file_exsists(trackPath):
		return send_no_file_error(trackPath)

	if currentTrack == None:
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
	
	destPos = check_integer(request, params.POSITION)
	unpause = True

	if destPos == None:
		return send_error(error_codes.WRONG_PLAYBACK_POSITION, "Wrong playback position")

	unpause = check_boolean(request, params.UNPAUSE)

	if currentTrack == None:
		return send_error(error_codes.NO_TRACK, "No track playing")
	elif destPos == -1:
		return send_error(error_codes.WRONG_PLAYBACK_POSITION, "No position specified")
	elif destPos < 0 or destPos > round(currentTrack.getLength() / 1000):
		return send_error(error_codes.WRONG_PLAYBACK_POSITION, "Wrong playback position. It should be specified with seconds")
	else:

		oldPos = currentTrack.playbackInfo().get('playback').get('position').get('millis')
		total = currentTrack.playbackInfo().get('playback').get('total').get('millis')
		currentTrack.setPlaybackPosition(destPos)

		if unpause and currentTrack.isPaused():
			currentTrack.unpause()

		return send_state_track_message(currentTrack, "Playback position succesfully changed", {
				'newPosition' : destPos * 1000,
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

	if currentTrack == None:
		return send_error(error_codes.NO_TRACK, "No track playing")
	elif not currentTrack.isPaused():
		return send_error(error_codes.TRACK_ALREADY_PLAYING, "Track is already playing")
	else:
		currentTrack.unpause()
		return send_state_track_message(currentTrack, "Track unpaused")

@app.route('/track/smartpause')
def smartpause_track():
	currentTrack = trackThreader.currentTrack()

	if currentTrack == None:
		return send_error(error_codes.NO_TRACK, "No track playing")
	
	if currentTrack.isPaused():
		currentTrack.unpause()
		return send_state_track_message(currentTrack, "Track unpaused")
	else:
		currentTrack.pause()
		return send_state_track_message(currentTrack, "Track paused")

@app.route('/track/metadata', methods=['GET'])
def metadata_track():
	currentTrack = trackThreader.currentTrack()
	if currentTrack != None:
		return jsonify(currentTrack.getMetadata())
	return send_error(error_codes.NO_TRACK, "No track playing")

@app.route('/track/playback', methods=['GET'])
def playback_track():
	currentTrack = trackThreader.currentTrack()
	if(currentTrack != None):
		response = currentTrack.playbackInfo()
		response['code'] = error_codes.SUCCESFULL_QUERY
		return jsonify(response)
	return send_error(error_codes.NO_TRACK, "No track playing")



@app.route('/track/online', methods=['GET'])
def track_online():
	currentTrack = trackThreader.currentTrack()
	if(currentTrack != None):
		response = currentTrack.playbackInfoExtended()
		response['code'] = error_codes.SUCCESFULL_QUERY
		return jsonify(response)
	return send_error(error_codes.NO_TRACK, "No track playing")

@app.route('/track/alive')
def alive_track():
	currentTrack = trackThreader.currentTrack()
	alive = currentTrack != None

	return jsonify({
			"code" : error_codes.SUCCESFULL_QUERY,
			"state" : alive
		})

@app.route('/track/stop')
def stop_track():
	currentTrack = trackThreader.currentTrack()
	if currentTrack != None:
		currentTrack.stop()
		trackThreader.setTrack(None)
		return jsonify({'message' : "Track stopped"})
	else:
		return send_error(error_codes.NO_TRACK, "No track playing")


# PLAYLIST SECTION

@app.route('/playlist/play', methods=['GET', 'POST'])
def play_playlist():
	currentPlaylist = playlistThreader.currentPlaylist()

	defaultPosition = check_integer(request, params.INDEX)
	terminate = check_boolean(request, params.TERMINATE)
	tracks = check_string_array(request, params.TRACK)

	#http://localhost:5000/playlist/play?track=tracks/track5.mp3&track=tracks/track2.mp3&track=tracks/track5.mp3&i=0&t=True

	if currentPlaylist == None:
		return startPlaylist(tracks, defaultPosition)
	else:

		if terminate:
			if currentPlaylist != None and currentPlaylist.currentTrack != None:
				currentPlaylist.stop()
				playlistThreader.setPlaylist(None)
				playlistThreader.reInit()
			return startPlaylist(tracks, defaultPosition)

		return send_error(error_codes.PLAYLIST_EXSIST, "Playlist already exsist")

@app.route('/playlist/next')
def playlist_next():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		if currentPlaylist.nextTrackAvilable():
			currentPlaylist.nextTrack(onPlaylistLoadError)
			return send_state_playlist_message(currentPlaylist, "Track succesfully changed")
		else:
			return send_error(error_codes.NO_NEXT_TRACK, "No next track avilable")
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")


@app.route('/playlist/prev')
def playlist_prev():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		if currentPlaylist.prevTrackAvilable():
			currentPlaylist.previousTrack(onPlaylistLoadError)
			return send_state_playlist_message(currentPlaylist, "Track succesfully changed")
		else:
			return send_error(error_codes.NO_PREV_TRACK, "No previous track avilable")
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")


@app.route('/playlist/rewind', methods=['GET', 'POST'])
def playlist_rewind():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None:
		currentTrack = currentPlaylist.currentTrack
		
		destPos = check_integer(request, params.POSITION)
		unpause = True

		if destPos == None:
			return send_error(error_codes.WRONG_PLAYBACK_POSITION, "Wrong playback position")

		unpause = check_boolean(request, params.UNPAUSE)

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

			return send_state_playlist_message(currentPlaylist, "Playback position succesfully changed", {
					'newPosition' : destPos,
					'oldPosition' : oldPos,
					'total' : total
				})
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")


@app.route('/playlist/pos', methods=['GET', 'POST'])
def playlist_pos():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		index = check_integer(request, params.INDEX)

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

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		return jsonify(currentPlaylist.playbackInfo(error_codes.SUCCESFULL_QUERY))
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")


@app.route('/playlist/pause')
def playlist_pause():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		currentTrack = currentPlaylist.currentTrack

		if(currentTrack == None):
			return send_error(error_codes.NO_TRACK, "No track playing")
		elif(currentTrack.isPaused()):
			return send_error(error_codes.TRACK_ALREADY_PAUSED, "Track is already paused")
		else:
			currentTrack.pause()
			return send_state_playlist_message(currentPlaylist, "Track paused")

	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")	


@app.route('/playlist/unpause')
def playlist_unpause():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		currentTrack = currentPlaylist.currentTrack

		if(currentTrack == None):
			return send_error(error_codes.NO_TRACK, "No track playing")
		elif not currentTrack.isPaused():
			return send_error(error_codes.TRACK_ALREADY_PLAYING, "Track is already playing")
		else:
			currentTrack.unpause()
			return send_state_playlist_message(currentPlaylist, "Track unpaused")

	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")

@app.route('/playlist/smartpause')
def playlist_smartpause():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		currentTrack = currentPlaylist.currentTrack

		if(currentTrack == None):
			return send_error(error_codes.NO_TRACK, "No track playing")

		if currentTrack.isPaused():
			currentTrack.unpause()
			return send_state_playlist_message(currentPlaylist, "Track unpaused")
		else:
			currentTrack.pause()
			return send_state_playlist_message(currentPlaylist, "Track paused")

	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")	

@app.route('/playlist/alive')
def playlist_alive():
	currentPlaylist = playlistThreader.currentPlaylist()
	alive = currentPlaylist != None

	return jsonify({
			"code" : error_codes.SUCCESFULL_QUERY,
			"state" : alive
		})

@app.route('/playlist/stop')
def stop_playlist():
	currentPlaylist = playlistThreader.currentPlaylist()

	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		currentPlaylist.stop()
		playlistThreader.setPlaylist(None)

		return jsonify({'message' : "Playlist stopped" })
	else:
		return send_error(error_codes.NO_PLAYLIST, "Playlist doesn't exsist")


#Config API actions
@app.route('/volume', methods = ['GET'])
def get_volume():
	value = check_float(request, params.VALUE)

	if value != None and value != "":
		vol_response = volumizer.setVolume(value)
		if vol_response != None:
			vol = vol_response['config']['milli']
			playlistThreader.setVolume(vol)
			trackThreader.setVolume(vol)

	respone = volumizer.getJSON()
	respone.update({"code" : error_codes.SUCCESFULL_QUERY})
	return jsonify(respone)

@app.route('/volume', methods = ['POST'])
def set_volume():
	respone = volumizer.setVolume(check_float(request, params.VALUE))

	if respone == None:
		return send_error(error_codes.INVALID_VALUE, "Invalid volume value. Only 0 - 100")

	respone.update({"code" : error_codes.SUCCESFULL_QUERY})

	vol = respone['config']['milli']
	playlistThreader.setVolume(vol)
	trackThreader.setVolume(vol)

	return jsonify(respone)

#Explore filesystem action
@app.route('/data', methods = ['GET', 'POST'])
def getDirectory():

	path = check_string(request, params.PATH)
	if path == None:
		path = get_defaults()['defaults']['default_path']

	metadata = check_boolean(request, params.METADATA)

	sortingMethod = check_integer(request, params.SORT)
	if sortingMethod == None:
		sortingMethod = check_string(request, params.SORT)
	sortingMethod = translate_sorting_method(sortingMethod, 0)

	respone = explorer.getPathContent(path, metadata, sorting = sortingMethod)
	if respone == None:
		return send_error(error_codes.INVALID_PATH, "Invalid path")

	respone['code'] = error_codes.SUCCESFULL_QUERY
	return jsonify(respone)

#Gets all tracks on file system(may be unefficient)
@app.route('/all_tracks', methods = ['GET', 'POST'])
def getAllTracks():

	simple = check_boolean(request, params.SIMPLE)
	local = check_boolean(request, params.LOCAL)
	initialPath = check_string(request, params.PATH)

	sortingMethod = check_integer(request, params.SORT)
	if sortingMethod == None:
		sortingMethod = check_string(request, params.SORT)
	sortingMethod = translate_sorting_method(sortingMethod, 1)

	if initialPath == None:
		initialPath = get_defaults()["defaults"]["default_path"]

	if not os.path.isdir(initialPath):
		return send_error(error_codes.INVALID_PATH, "Invalid path")

	respone = explorer.getAllTracks(initialPath, sortingMethod, simple, local)
	
	if not 'error' in respone:
		respone['code'] = error_codes.SUCCESFULL_QUERY

	return jsonify(respone)

@app.route('/all_playlists', methods = ['GET', 'POST'])
def getAllPlaylists():

	local = check_boolean(request, params.LOCAL)
	sortingMethod = check_integer(request, params.SORT)
	if sortingMethod == None:
		sortingMethod = check_string(request, params.SORT)
	sortingMethod = translate_sorting_method(sortingMethod)

	trackSortingMethod = check_integer(request, params.TRACK_SORT)
	if trackSortingMethod == None:
		trackSortingMethod = check_string(request, params.TRACK_SORT)
	trackSortingMethod = translate_sorting_method(trackSortingMethod, 1)

	filters = check_int_array(request, params.FILTER)
	if len(filters) == 0:
		filters.append(0) #0 means no filtering

	initialPath = check_string(request, params.PATH)

	if initialPath == None:
		initialPath = get_defaults()["defaults"]["default_path"]

	if not os.path.isdir(initialPath):
		return send_error(error_codes.INVALID_PATH, "Invalid path")

	respone = explorer.getAllPlaylists(initialPath, sortingMethod, trackSortingMethod, filters, local)
	
	if not 'error' in respone:
		respone['code'] = error_codes.SUCCESFULL_QUERY

	return jsonify(respone)

@app.route('/metadata', methods = ['GET'])
def get_metadata():
	path = check_string(request, params.PATH)

	if path == None:
		return send_error(error_codes.INVALID_PATH, "You need to specify path parameter")

	if not file_exsists(path):
		return send_no_file_error(path)

	respone = explorer.getMetadata(path)
	respone['code'] = error_codes.SUCCESFULL_QUERY

	return jsonify(respone)

@app.route('/defaults', methods = ['GET'])
def defaults():
	return jsonify(get_defaults())


#Flush every aduio stream
@app.route('/flush', methods = ['GET', 'POST'])
def flush():

	flushTrack()
	flushPlaylist()

	return jsonify({
		"code" : error_codes.SUCCESFULL_QUERY,
		"message" : "flushed"
		})

@app.route('/test', methods = ['GET'])
def test():
	return jsonify(
			{
				"code" : error_codes.SUCCESFULL_QUERY,
				"message" : "Seems to be working fine"
			}
		)

#Path for serving local files
@app.route('/file', methods = ['GET'])
def send_audio():
	path = check_string(request, params.PATH)

	if path == None:
		return send_error(error_codes.INVALID_PATH, "You need to specify path parameter")
	if not file_exsists(path):
		return send_no_file_error(path)

	return send_from_directory(directory = os.path.dirname(path), filename = os.path.basename(path))	


@app.route('/file/upload', methods = ['POST'])
def file_upload():
	path = check_string(request, params.PATH)
	if path == None:
		return send_error(error_codes.INVALID_PATH, "You need to specify path parameter")
	if not os.path.isdir(path):
		return send_no_dir_error(path)

	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file_path = os.path.join(path, filename)
		file.save(file_path)
		return jsonify({
			"code" : error_codes.SUCCESFULL_QUERY,
			"path" : file_path,
			"message" : "File uploaded"
			})

	return jsonify({
			"code" : error_codes.UNALLOWED_EXTENSION,
			"message" : "Unallowed extension"
		})

@app.route('/file/delete', methods = ['GET', 'POST'])
def file_delete():
	path = check_string(request, params.PATH)

	if path == None:
		return send_error(error_codes.INVALID_PATH, "You need to specify path parameter")
	if not os.path.exists(path):
		return send_no_file_error(path)

	try:
		if(os.path.isdir(path)):
			shutil.rmtree(path)
		else:
			os.remove(path)
		return jsonify({
			"code" : error_codes.SUCCESFULL_QUERY,
			"message" : "File/directory deleted"
		})
	except:
		return jsonify({
			"code" : error_codes.DATA_MANAGEMENT_ERROR,
			"message" : "An error while deleting file has occured"
		})

#Utility methods
def flushTrack():
	currentTrack = trackThreader.currentTrack()
	if currentTrack != None:
		currentTrack.stop()
	trackThreader.setTrack(None)
	flush_stream()


def flushPlaylist():
	currentPlaylist = playlistThreader.currentPlaylist()
	if currentPlaylist != None and currentPlaylist.currentTrack != None:
		currentPlaylist.stop()
	playlistThreader.setPlaylist(None)
	flush_stream()


def startTrack(trackPath):
	#trackThreader.registerOnEndCustomCallback(track_endevent)

	if(trackPath == "" or trackPath == None):
		return send_error(error_codes.NO_PATH_DEFINED, "No path parameter passed.")

	if not os.path.exists(trackPath):
		return send_error(error_codes.WRONG_PATH_SPECIFIED, "File doesn't exsist.")

	if not is_valid_file(trackPath):
		return send_error(error_codes.INVALID_TYPE, "Invalid filetype.")

	flushPlaylist()
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

		if len(tracks) == 0:
			return send_error(error_codes.NO_PATH_DEFINED, "No track parameter passed.")

		errorPos = []
		for index, trackPath in enumerate(tracks):

			if not os.path.exists(trackPath):
				errorPos.append({"index" : index})
				errorPos[-1].update(send_error(error_codes.WRONG_PATH_SPECIFIED, "File doesn't exsist.", False))
				continue

			if not is_valid_file(trackPath):
				errorPos.append({"index" : index})
				errorPos[-1].update(send_error(error_codes.INVALID_TYPE, "Invalid filetype.", False))
				continue

		if len(errorPos) > 0:
			return send_playlist_play_error(errorPos, "Invalid track array")

		flushTrack()
		currentPlaylist = data.get('playlist')

		playlistThreader.startThread()

		return send_state_playlist_message(currentPlaylist, "Playlist succesfully started", None, 1, False)


def onPlaylistLoadError():
	playlistThreader.setPlaylist(None)	

	return send_error(error_codes.INVALID_PATH, "Path error occured. Removing playlist...")

if __name__ == '__main__':
    app.run(debug=True, threaded = True)
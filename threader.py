from playlist import Playlist
from track import Track
import threading
from queue import Queue


class TrackThreader():
	def __init__(self):
		self.playingThread = None
		self.track = None
		self.onEndCustomCallback = None

	def __play_track(self, track, callback = None):
		if(callback == None):
			track.play()
		else:
			callback(track)
		self.__oversee_track(track)
	
	#This makes track to disapear after it's done playing
	def __oversee_track(self, track):
		while track.isBusy():
			continue
		if(self.onEndCustomCallback == None):
			if(self.track != None):
				print(self.track.getPath() + " finished playing.")
			self.setTrack(None)
		else:
			self.__play_track(track, self.onEndCustomCallback)

	def getThread(self, path):
		self.track = Track(path)
		self.playingThread = threading.Thread(target = self.__play_track, args=(self.track, ))
		self.playingThread.daemon = True
		return {'thread' : self.playingThread,
				'track' : self.track}

	def currentTrack(self):
		return self.track

	def setTrack(self, track):
		self.track = track

	def registerOnEndCustomCallback(self, callback):
		self.onEndCustomCallback = callback

class PlaylistThreader():
	def __init__(self):
		self.playingThread = None
		self.playlist = None
		self.nextTrack = False
		self.prevTrack = True

	def __play_playlist(self, position = 0):
		self.playlist.play(position)
		self.__oversee_playlist()

	def __oversee_playlist(self):

		while True:
			try:
				if self.playlist.nextTrackAvilable() and self.playlist.shouldGoNext():
					print("NEXT TRACK!")
					self.playlist.nextTrack()
				if not self.playlist.nextTrackAvilable() and self.playlist.shouldGoNext():
					print("Playlist finished playing")
					self.setPlaylist(None)
					break
			except:
				self.setPlaylist(None)
				break


	def getThread(self, tracks, position = 0):
		self.playlist = Playlist(tracks)
		self.playingThread = threading.Thread(target = self.__play_playlist, args=(position,))
		self.playingThread.daemon = True
		return {'thread' : self.playingThread,
				'playlist' : self.playlist}

	def currentPlaylist(self):
		return self.playlist

	def setPlaylist(self, playlist):
		self.playlist = playlist

	def skipTrack(self):
		self.nextTrack = True

	def previousTrack(self):
		self.prevTrack = True


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

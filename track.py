from pygame import mixer
from datetime import datetime
import math
import time
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
import ntpath
import os

class Track:

	def __init__(self, path, volume = 1.0):
		self.mixer = mixer
		self.trackPath = path
		self.extension = self.__getExtension(self.trackPath)
		self.mixer.init()
		self.setVolume(volume)
		self.loadTrack(path)

	def reInit(self):
		self.playbackOffset = 0
		self.paused = False

	def loadTrack(self, path):
		self.trackPath = path
		self.extension = self.__getExtension(self.trackPath)
		self.mixer.music.load(path)
		self.reInit()

	def play(self):
		self.mixer.music.play()

	def stop(self):
		self.mixer.music.stop()

	def pause(self):
		self.paused = True
		self.mixer.music.pause()

	def unpause(self):
		self.paused = False
		self.mixer.music.unpause()

	def isPaused(self):
		return self.paused

	def restart(self):
		self.stop()
		self.play()

	def isPlaying(self):
		if not self.isPaused():
			return self.mixer.music.get_busy()
		return int(self.isPaused == 'false')

	def isBusy(self):
		return self.mixer.music.get_busy()

	def getVolume(self):
		return self.mixer.music.get_volume()

	def setVolume(self, volume):
		if(volume > 1):
			volume = 1
		elif(volume < 0):
			volume = 0
		self.mixer.music.set_volume(volume)

	def getPlaybackPosition(self):
		return self.mixer.music.get_pos() + self.playbackOffset

	def setPlaybackPosition(self, secs):
		curPlaybackPos = self.getPlaybackPosition()
		millis = secs * 1000
		if(millis > curPlaybackPos):
			self.playbackOffset += millis - curPlaybackPos
		if(millis < curPlaybackPos):
			self.playbackOffset -= curPlaybackPos - millis

		self.mixer.music.set_pos(secs)

	def getLength(self):
		audio = None
		if self.extension == ".mp3":
			audio = MP3(self.trackPath)
		elif self.extension == ".flac":
			audio = FLAC(self.trackPath)
		return audio.info.length * 1000

	def dispose(self):
		self.mixer.quit()

	def getPath(self):
		return self.trackPath

	def formattedTimestamp(self, millis = -1):
		if millis == -1:
			millis = self.getPlaybackPosition()
		secs = round(millis / 1000.0)
		mins = math.floor(secs / 60)
		secs -= mins * 60

		if(mins < 0 or secs < 0):
			return "00:00"

		strSecs = str(secs)
		strMins = str(mins)

		if(secs < 10):
			strSecs = "0" + strSecs
		if(mins < 10):
			strMins = "0" + strMins

		return strMins + ":" + strSecs

	def playbackInfo(self):
		return { 'playback' : {
				'playing' : self.isPlaying(),
				'paused' : self.isPaused(),
				'path' : self.trackPath,
				'position' : {
					'millis' : self.getPlaybackPosition(),
					'secs' : round(self.getPlaybackPosition() / 1000),
					'formatted' : self.formattedTimestamp()
				},

				'total' : {
					'millis' : self.getLength(),
					'secs' : round(self.getLength()/1000),
					'formatted' : self.formattedTimestamp(self.getLength())
				}
			}
		}

	def getMetadata(self):

		artistName = None
		albumName = None
		trackGenre = None
		trackTitle = ntpath.basename(self.__path_leaf(self.getPath()))
		trackLength = -1

		if(self.extension == ".mp3"):
			audio = MP3(self.getPath())
		elif(self.extension == ".flac"):
			audio = FLAC(self.getPath())

		artistName = audio['artist'][0] if 'artist' in audio  else artistName
		albumName = audio['album'][0] if 'album' in audio else albumName
		trackTitle = audio['title'][0] if 'title' in audio else trackTitle
		trackGenre = audio['genre'][0] if 'genre' in audio else trackGenre
		trackLength = audio.info.length * 1000.0

		return {'metadata' : { 
					'artist' : artistName,
					'album' : albumName,
					'title' : trackTitle,
					'genre' : trackGenre,
					'length' : round(trackLength) 
				}}

	def setEndevent(self, callback):
		self.mixer.music.set_endevent(callback)

	def __getExtension(self, path):
		return os.path.splitext(path)[1]

	def __path_leaf(self, path):
		head, tail = ntpath.split(path)
		return tail or ntpath.basename(head)

	def __current_milli_time(self):
		return int(round(time.time() * 1000))
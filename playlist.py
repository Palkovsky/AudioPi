from track import Track

class Playlist:

	def __init__(self, tracks, volume = 1):
		self.position = -1
		self.threadCount = len(tracks)
		self.volume = volume
		self.currentTrack = None
		self.tracks = tracks

	def loadTracks(self, tracks):
		self.tracks = tracks
		self.threadCount = len(tracks)

	def play(self, position = 0):
		if len(self.tracks) > 0 and len(self.tracks) > position:
			self.position = position
			self.currentTrack = Track(self.tracks[self.position])
			self.currentTrack.setVolume(self.volume)
			self.currentTrack.play()
		else:
			raise IndexError('Wrong track position')

	def nextTrack(self):
		self.play(self.position + 1)
		#self.threadCount += 1

	def previousTrack(self):
		self.play(self.position - 1)
		#self.threadCount += 1

	def nextTrackAvilable(self):
		if len(self.tracks) > self.position + 1:
			return True
		return False

	def prevTrackAvilable(self):
		if len(self.tracks) > 0 and self.position - 1 >= 0:
			return True
		return False

	def setVolume(self, volume):
		if(volume > 1):
			volume = 1
		elif(volume < 0):
			volume = 0
		self.volume = volume
		self.currentTrack.setVolume(volume)

	def pause(self):
		self.currentTrack.pause()

	def unpause(self):
		self.currentTrack.unpause()

	def stop(self):
		self.currentTrack.stop()

	def isPaused(self):
		return self.currentTrack.isPaused()

	def getVolume(self):
		return self.volume

	def isPlaying(self):
		if self.currentTrack != None:
			return self.currentTrack.isPlaying()
		return None

	def isPaused(self):
		if self.currentTrack != None:
			return self.currentTrack.isPaused()
		return None


	def getPosition(self):
		return self.position;

	def dispose(self):
		self.currentTrack.dispose()

	def onTrackEnd(self, callback):
		callback(self.position)

	def getTracks(self):
		return self.tracks

	def playbackInfo(self, code):

		base_response = {
							'code' : code,
							'position' : self.position,
							'total' : len(self.tracks)
						}

		base_response.update(self.currentTrack.playbackInfo())

		response = {'playlist' : base_response }

		return response

	def shouldGoNext(self):
		data = self.currentTrack.playbackInfo()
		current = data.get('playback').get('position').get('millis')
		total = data.get('playback').get('total').get('millis')

		if current >= total:
			return True
		return False
from track import Track

class Playlist:

	def __init__(self, tracks):
		self.position = -1
		self.currentTrack = None
		self.tracks = tracks

	def loadTracks(self, tracks):
		self.tracks = tracks

	def play(self, position = 0):
		if len(self.tracks) > 0 and len(self.tracks) > position:

			if(self.currentTrack != None):
				self.currentTrack.dispose()

			self.position = position
			self.currentTrack = Track(self.tracks[self.position])
			self.currentTrack.play()
		else:
			raise IndexError('Wrong track position')

	def nextTrack(self):
		if len(self.tracks) > self.position + 1:
			self.play(self.position + 1)
			return True
		return False

	def previousTrack(self):
		if self.position > 0 and len(self.tracks) > 0:
			self.play(self.position - 1)
			return True
		return False

	def isPlaying(self):
		return self.currentTrack.isPlaying()

	def getPosition(self):
		return self.position;

	def dispose(self):
		self.currentTrack.dispose()

	def onTrackEnd(self, callback):
		callback(self.position)
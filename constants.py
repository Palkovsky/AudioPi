
class Globals():

	def __init__(self):

		#ERRORS
		self.NO_TRACK = 1015
		self.TRACK_ALREADY_PAUSED = 1016
		self.TRACK_ALREADY_PLAYING = 1017
		self.NO_PATH_DEFINED = 1018
		self.WRONG_PATH_SPECIFIED = 1019
		self.INVALID_TYPE = 1020
		self.WRONG_PLAYBACK_POSITION = 1021

		self.NO_PLAYLIST = 1030
		self.PLAYLIST_EXSIST = 1031
		self.WRONG_TRACK_INDEX = 1032
		self.NO_NEXT_TRACK = 1035
		self.NO_PREV_TRACK = 1036
		self.INVALID_TRACK_INDEX = 1037

		#OTHERS
		self.SUCCESFULL_QUERY = 999
		

error_codes = Globals()
whitelisted_extensions = ['.flac', '.mp3']
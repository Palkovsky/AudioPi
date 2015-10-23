
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

		#OTHERS
		self.SUCCESFULL_QUERY = 999
		

error_codes = Globals()
whitelisted_extensions = ['.flac', '.mp3']
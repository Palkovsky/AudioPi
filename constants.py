
class ErrorGlobals():

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
		self.INVALID_TRACKS = 1038


		#VOLUME
		self.INVALID_VALUE = 1069


		#OTHERS
		self.SUCCESFULL_QUERY = 999
		
class ParamGlobals(object):

	def __init__(self):
		
		self.PATH = "p"
		self.TERMINATE = "t"
		self.VALUE = "value"
		self.POSITION = "pos"
		self.INDEX = "i"
		self.UNPAUSE = "unpause"

		self.TRACK = "track"
		

error_codes = ErrorGlobals()
params = ParamGlobals()
whitelisted_extensions = ['.flac', '.mp3']
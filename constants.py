import getpass

#these weird structures should be replaced with dicts

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
		self.REQUEST_TIMEOUT = 500
		self.UPLOAD_ERROR = 501
		self.UNALLOWED_EXTENSION = 502

		#Paths
		self.PATH_EMPTY = 1100
		self.INVALID_PATH = 1101
		self.FILE_NOT_EXSISTS = 1102
		self.DIR_NOT_EXSIST = 1103

		self.UNDEFINED = 111
		
class ParamGlobals():

	def __init__(self):
		self.TERMINATE = "t"
		self.VALUE = "value"
		self.POSITION = "pos"
		self.INDEX = "i"
		self.UNPAUSE = "unpause"

		self.TRACK = "track"
		self.PATH = "path"
		self.FILTER = "filter"
		self.SIMPLE = "simple"
		self.SORT = "sort"
		self.TRACK_SORT = "tsort"
		self.METADATA = "meta"
		self.LOCAL = "local"

class Defaults():
	def __init__(self):
		self.path = '/media'

class PlaylistFilters():
	
	def __init__(self):
		self.NO_FILTERING = 0
		self.ALBUMS_ONLY = 1
		self.ARTISTS_ONLY = 2
		self.GENRES_ONLY = 3
		self.UNKNOWN_ONLY = 4
		self.INCLUDE_ALL = 5

class Limits(object):
	def __init__(self):
		self.MAX_REQUEST_TIME = 36


		

error_codes = ErrorGlobals()
params = ParamGlobals()
defaults = Defaults()
playlist_filters = PlaylistFilters()
limits = Limits()
sorting_methods = [
	{"name" : "normal", "value" : 0},
	{"name" : "name", "value" : 1},
	{"name" : "length", "value" : 2},
	{"name" : "name_desc", "value" : 3},
	{"name" : "length_asc", "value" : 4}
]
whitelisted_extensions = ['.flac', '.mp3', '.ogg']
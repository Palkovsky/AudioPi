Little project, which will allow to control Raspberry Pi over Internet.


/track/play [POST, GET]
	GET: p(path), t(terminate)
		p is path to the audio track
		if 't' == True => terminate current track
	POST: p(path), t(terminate)
		UP

/track/smartpause | /playlist/smartpause [GET]
	It pauses or unpauses current audio stream based on
	current state. If audio was paused, this method would unpause it.

/playlist/play [POST, GET]
	- i(ndex) = default position
	- tracks = array of track paths
	- t(erminate) = do you want to terminate current playlist


/playlist/pos [POST, GET]
	-i(ndex) = position of track

/playlist/rewind [POST, GET]
	-pos



/volume [GET]
	Gets current volume

/volume [POST]
	Sets current volume
	-value


	SORTING
	{"name" : "normal", "value" : 0},
	{"name" : "name", "value" : 1},
	{"name" : "length", "value" : 2},
	{"name" : "name_desc", "value" : 3},
	{"name" : "length_asc", "value" : 4}
	When passing sort, tsort param you can give 'name' or 'value' value. It'll be properly parsed and served.

/data [POST, GET]
	-path = path to explore
	-meta = get additional metadata if true
	-sort, supports only 1 and 3

Gets all tracks on the filesystem
/all_tracks [GET]
	-simple - boolean - default FALSE. Provides more information about tracks if FALSE, but with
						TRUE feed is a little bit lighter

	-path - /all_tracks by default starts looking for playlists in your default path('/media/[username]'), then goes deaper, with
		this argument you can choose initial path from which recursive search will be fired

	-sort - every sorting method avilable - DEFAULT: 1
	-local(bool) - if true don't scan every dir recursively

This action gets all tracks on the filesystem and arranges them into playlists via ID3 tags
/all_playlists [GET]
	-filter = optional argument. It's int array You pass in array values to customize your feed.
	
	So if for example you want only playlists by artists and gentes you pass array [2, 3], for only
	albums you'd pass [1]

	If you've passed NO_FILTERING[0] other filter values are ignored.

	INCLUDE_ALL is as default disabled, it append to response all tracks as playlist.

	NO_FILTERING = 0
	ALBUMS_ONLY = 1
	ARTISTS_ONLY = 2
	GENRES_ONLY = 3
	UNKNOWN_ONLY = 4
	INCLUDE_ALL = 5
	//Unknown is playlist containg tracks without artist and album(from ID3 tag, ofc)

	-path - /all_playlists by default starts looking for playlists in default path, then goes deaper, with
			this argument you can choose initial path from which recursive search will be fired


	-sort - only 1(by name) and 3(by name desc) avilable, because playlist doesn't have track length - DEFAULT: 0
	-tsort - track sort method, every method avilable - DEFAULT: 1
	-local(bool) - if true don't scan every dir recursively

/metadata [GET]
	-path (path to audio file from which we want to export metadata)

ERROR CODES:
		NO_TRACK = 1015
		TRACK_ALREADY_PAUSED = 1016
		TRACK_ALREADY_PLAYING = 1017
		NO_PATH_DEFINED = 1018
		WRONG_PATH_SPECIFIED = 1019
		INVALID_TYPE = 1020
		WRONG_PLAYBACK_POSITION = 1021

		NO_PLAYLIST = 1030
		PLAYLIST_EXSIST = 1031
		WRONG_TRACK_INDEX = 1032
		NO_NEXT_TRACK = 1035
		NO_PREV_TRACK = 1036
		INVALID_TRACK_INDEX = 1037
		INVALID_TRACKS = 1038

		#VOLUME
		INVALID_VALUE = 1069

		#OTHERS
		SUCCESFULL_QUERY = 999
		REQUEST_TIMEOUT = 500

		#Paths
		PATH_EMPTY = 1100
		INVALID_PATH = 1101
		FILE_NOT_EXSISTS = 1102

		UNDEFINED = 111
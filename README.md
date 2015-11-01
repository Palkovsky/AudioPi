Little project, which will allow to control Raspberry Pi over Internet.


/track/play [POST, GET]
	GET: p(path), t(terminate)
		p is path to the audio track
		if 't' == True => terminate current track
	POST: p(path), t(terminate)
		UP

/playlist/play [POST, GET]
	- i(ndex) = default position
	- tracks = array of track paths
	- t(erminate) = do you want to terminate current playlist


/playlist/pos [POST, GET]
	-i(ndex) = position of track

/playlist/rewind [POST, GET]
	-pos

/data [POST, GET]
	-path = path to explore

/volume [GET]
	Gets current volume

/volume [POST]
	Sets current volume
	-value

Gets all tracks on the filesystem
/all_tracks [GET]

This action gets all tracks on the filesystem and arranges them into playlists via ID3 tags
/all_playlists [GET]
	-filter = optional argument. It's int array You pass in array values to customize your feed.
	
	So if for example you want only playlists by artists and gentes you pass array [2, 3], for only
	albums you'd pass [1]

	If you've passed NO_FILTERING[0] other filter values are ignored.

	NO_FILTERING = 0
	ALBUMS_ONLY = 1
	ARTISTS_ONLY = 2
	GENRES_ONLY = 3
	UNKNOWN_ONLY = 4
	//Unknown is playlist containg tracks without artist and album(from ID3 tag, ofc)

TO DO:
	-exception handling with not exsiting tracks
	-fix __get_cover method in explore.py
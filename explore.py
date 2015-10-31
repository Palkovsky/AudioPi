import os
import glob
from constants import whitelisted_extensions, defaults, playlist_filters
from mutagen import File

class Explorer():

	def __init__(self):
		self.__default_path = defaults.path
		self.__PLAYLIST_TYPE_ARTIST = "artist"
		self.__PLAYLIST_TYPE_ALBUM = "album"
		self.__UNDEFINED_PLAYLIST_NAME = "Unknown"
		self.__filters = [playlist_filters.NO_FILTERING, playlist_filters.ARTISTS_ONLY,
						playlist_filters.ALBUMS_ONLY, playlist_filters.ARTISTS_AND_ALBUMS,
						playlist_filters.UNKNOWN_ONLY]

	def getPathContent(self, path):

		if path == None:
			return None

		if not os.path.isdir(path):
			return None

		path = self.__path_leaf(path)

		if not path.startswith(self.__default_path):
			return None

		directories_list = []

		for directory in self.__get_immediate_subdirectories(path):
			if directory[0] != ".":
				directories_list.append({"relative" : directory,
										"full" : os.path.join(path, directory)})

		files_list = []
		files = []

		for ext in whitelisted_extensions:
			files += glob.glob(path + '/*' + ext)

		for f in files:
			basename = os.path.basename(f)
			files_list.append({
					"relative" : basename,
					"full" : f,
					"simple" : os.path.splitext(basename)[0]
			})


		upDir = os.path.dirname(path)
		if path == self.__default_path:
			upDir = None


		return {
			"directory" : {
				"path" : path,
				"upDir" : upDir,
				"directories" : directories_list,
				"tracks" : files_list
			}
		}

	def getAllTracks(self, simple = False):

		files_list = []

		for dirpath, dirnames, filenames in os.walk(self.__default_path):
			for filename in [f for f in filenames if self.__isWhitelisted(f)]:
				fullPath = os.path.join(dirpath, filename)
				basename = os.path.basename(fullPath)

				if not simple:
					f = File(fullPath)
					artist = f['artist'][0] if 'artist' in f else None
					album = f['album'][0] if 'album' in f else None
	
					files_list.append({
						"basename" : basename,
						"full" : fullPath,
						"simple" : os.path.splitext(basename)[0],
						"artist" : artist,
						"album" : album
					})

				else:

					files_list.append({
						"basename" : basename,
						"full" : fullPath,
						"simple" : os.path.splitext(basename)[0],
					})					

		return {
			"tracks" : files_list
		}

	#Getting playlists via id3 tags
	def getAllPlaylists(self, filt = playlist_filters.NO_FILTERING):

		#Apply filters like:
		'''
			- albums only
			- artists only
			- unknown only
			- no unknown
		'''

		if not filt in self.__filters:
			filt = 0

		playlists = []
		albums = []
		artists = []
		tracks = self.getAllTracks(True)['tracks']

		for track in tracks:
			path = track['full']
			f = File(path)

			artist = f['artist'][0] if 'artist' in f else None
			album = f['album'][0] if 'album' in f else None

			if not artist in artists and artist != None:
				artists.append(artist)

			if not album in albums and album != None:
				albums.append(album)

			playlistsExsists = False
			#By artist
			if artist != None and (filt == playlist_filters.NO_FILTERING 
				or filt == playlist_filters.ARTISTS_ONLY or filt == playlist_filters.ARTISTS_AND_ALBUMS):
				for index, playlist in enumerate(playlists):
					if playlist['name'] == artist and playlist['type'] == self.__PLAYLIST_TYPE_ARTIST:
						playlist['tracks'].append(track)
						playlistsExsists = True
						break

				if len(playlists) == 0 or not playlistsExsists:
					playlists.append({
						"name" : artist,
						"artist" : artist,
						"album" : album,
						"type" : self.__PLAYLIST_TYPE_ARTIST,
						"tracks" : [track]
					})

			playlistsExsists = False

			#By album
			if album != None and (filt == playlist_filters.NO_FILTERING or filt == playlist_filters.ALBUMS_ONLY 
				or filt == playlist_filters.ARTISTS_AND_ALBUMS):
				for index, playlist in enumerate(playlists):
					if playlist['name'] == album and playlist['type'] == self.__PLAYLIST_TYPE_ALBUM:
						playlist['tracks'].append(track)
						playlistsExsists = True
						break

				if len(playlists) == 0 or not playlistsExsists:
					playlists.append({
						"name" : album,
						"artist" : artist,
						"album" : album,
						"type" : self.__PLAYLIST_TYPE_ALBUM,
						"tracks" : [track]
					})

			#Unknown
			if album == None and artist == None and (filt == playlist_filters.NO_FILTERING 
				or filt == playlist_filters.UNKNOWN_ONLY):
				for index, playlist in enumerate(playlists):
					if playlist['name'] == self.__UNDEFINED_PLAYLIST_NAME and playlist['type'] == None:
						playlist['tracks'].append(track)
						playlistsExsists = True
						break

				if len(playlists) == 0 or not playlistsExsists:
					playlists.append({
						"name" : self.__UNDEFINED_PLAYLIST_NAME,
						"artist" : None,
						"album" : None,
						"type" : None,
						"tracks" : [track]
					})


		return {"playlists" : playlists}


	def __get_immediate_subdirectories(self, a_dir):
	    return [name for name in os.listdir(a_dir)
	            if os.path.isdir(os.path.join(a_dir, name))]

	def __path_leaf(self, path):
		if path.endswith('/'):
			return path[:-1]
		return path

	def __isWhitelisted(self, path):
		for ext in whitelisted_extensions:
			if os.path.splitext(path)[1] == ext:
				return True
		return False

	def __getCover(self, file_path):
		path = self.__path_leaf(file_path)
		if not os.path.isfile(path) or not self.__isWhitelisted(path):
			return None

		f = File(path)
		#artwork = f.tags['APIC:'].data if 'APIC:' in f else None

		'''
		if artwork != None:
			artworkPath = 'resources/images/covers/' + os.path.basename(path) + '.jpg'
			with open(artworkPath, 'wb') as img:
				img.write(artwork) # write artwork to new image
			return artworkPath
		'''

		return None
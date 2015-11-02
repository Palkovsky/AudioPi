import os
import glob
from constants import whitelisted_extensions, defaults, playlist_filters
from mutagen import File

class Explorer():

	def __init__(self):
		self.__default_path = defaults.path

		self.__PLAYLIST_TYPE_ARTIST = "artist"
		self.__PLAYLIST_TYPE_ALBUM = "album"
		self.__PLAYLIST_TYPE_GENRE = "genre"
		self.__PLAYLIST_TYPE_ALL = "all"
		self.__UNDEFINED_PLAYLIST_TYPE = "Unknown"

		f = playlist_filters

		self.__ARTISTS_ALLOWED_FILTERS = [f.NO_FILTERING, f.ARTISTS_ONLY]
		self.__ALBUMS_ALLOWED_FILTERS = [f.NO_FILTERING, f.ALBUMS_ONLY]
		self.__GENRES_ALLOWED_FILTERS = [f.NO_FILTERING, f.GENRES_ONLY]
		self.__UNDEFINED_ALLOWED_FILTERS = [f.NO_FILTERING, f.UNKNOWN_ONLY]
		self.__ALL_ALLOWED_FILTERS = [f.INCLUDE_ALL]

		self.__filters = [f.NO_FILTERING, f.ARTISTS_ONLY, f.ALBUMS_ONLY, f.GENRES_ONLY,
						f.UNKNOWN_ONLY, f.INCLUDE_ALL]

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

	def getAllTracks(self, initialPath, simple = False):

		files_list = []

		for dirpath, dirnames, filenames in os.walk(initialPath):
			for filename in [f for f in filenames if self.__isWhitelisted(f)]:
				fullPath = os.path.join(dirpath, filename)
				basename = os.path.basename(fullPath)

				f = File(fullPath)
				if not simple:
					artist = f['artist'][0] if 'artist' in f else None
					album = f['album'][0] if 'album' in f else None
					genre = f['genre'][0] if 'genre' in f else None
					cover = self.__getCover(fullPath)
	
					files_list.append({
						"basename" : basename,
						"full" : fullPath,
						"simple" : os.path.splitext(basename)[0],
						"artist" : artist,
						"album" : album,
						"genre" : genre,
						"cover" : cover,
						"length" : round(f.info.length)
					})

				else:

					files_list.append({
						"basename" : basename,
						"full" : fullPath,
						"simple" : os.path.splitext(basename)[0],
						"length" : round(f.info.length)
					})					

		return {
			"tracks" : files_list
		}

	#Getting playlists via id3 tags
	def getAllPlaylists(self, initialPath, filt = [playlist_filters.NO_FILTERING]):

		#Apply filters like:
		'''
			- albums only
			- artists only
			- unknown only
			- no unknown
		'''

		if len(filt) <= 0:
			filt.append(playlist_filters.NO_FILTERING)

		for i in range(len(filt) - 1):
			if not filt[i] in self.__filters:
				filt[i] = playlist_filters.NO_FILTERING

		playlists = []
		albums = []
		artists = []
		genres = []
		tracks = self.getAllTracks(initialPath, True)['tracks']

		for track in tracks:
			path = track['full']
			f = File(path)

			artist = f['artist'][0] if 'artist' in f else None
			album = f['album'][0] if 'album' in f else None
			genre = f['genre'][0] if 'genre' in f else None

			if not artist in artists and artist != None:
				artists.append(artist)

			if not album in albums and album != None:
				albums.append(album)

			if not genre in genres and genre != None:
				genres.append(genre)

			trackInfo = {
				"path" : track,
				"artist" : artist,
				"album" : album,
				"genre" : genre,
				"cover" : self.__getCover(path)
			}

			#By artist
			if artist != None and self.__isAllowed(self.__PLAYLIST_TYPE_ARTIST, filt):
				self.__addTrack(playlists, artist, trackInfo, self.__PLAYLIST_TYPE_ARTIST)


			#By album
			if album != None and self.__isAllowed(self.__PLAYLIST_TYPE_ALBUM, filt):
				self.__addTrack(playlists, album, trackInfo, self.__PLAYLIST_TYPE_ALBUM)

			#By genre
			if genre != None and self.__isAllowed(self.__PLAYLIST_TYPE_GENRE, filt):
				self.__addTrack(playlists, genre, trackInfo, self.__PLAYLIST_TYPE_GENRE)

			#Unknown
			if album == None and artist == None and genre == None and self.__isAllowed(self.__UNDEFINED_PLAYLIST_TYPE, filt):
				self.__addTrack(playlists, self.__UNDEFINED_PLAYLIST_TYPE, trackInfo, self.__UNDEFINED_PLAYLIST_TYPE)

			#all
			if self.__isAllowed(self.__PLAYLIST_TYPE_ALL, filt):
				self.__addTrack(playlists, self.__PLAYLIST_TYPE_ALL, trackInfo, self.__PLAYLIST_TYPE_ALL)

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

	#This method will find and create cover of an album on device
	#It names album arts with this pattern : [Artist] - [Album].jpg
	def __getCover(self, file_path):
		path = self.__path_leaf(file_path)
		if not os.path.isfile(path) or not self.__isWhitelisted(path):
			return None

		f = File(path)
		artist = f['artist'][0] if 'artist' in f else None
		album = f['album'][0] if 'album' in f else None
		cover = None

		#audio.pictures, audio['covr'] and audio['APIC:']
		cover = f['covr'] if 'covr' in f else None
		if cover == None:
			cover = f['APIC:'] if 'APIC:' in f else None
		try:
			if cover == None:
				cover = f.pictures[0] if len(f.pictures) > 0 else None
		except:
			pass
		if cover == None:
			return cover

		dir_path = os.path.dirname(path)
		if artist != None and album != None:
			cover_filename = artist + " - " + album + ".jpg"
		elif artist == None and album != None:
			cover_filename = album + ".jpg"
		elif artist != None and album == None:
			cover_filename = artist + ".jpg"
		else:
			cover_filename = os.path.splitext(os.path.basename(path))[0] + "_cover.jpg"

		end_path = dir_path + "/" + cover_filename

		if not os.path.exists(end_path): #Don't recreate it every query. Do it only when there's no jpg cover
			picture_data = cover.data

			with open(end_path, 'wb') as img:
				img.write(picture_data)
		return end_path

	def __isAllowed(self, type, filters):

		allowedFilters = self.__getFilteringTable(type)

		if allowedFilters == None:
			return False

		allow = False
		for filter in allowedFilters:
			if filter in filters:
				allow = True

		return allow

	def __getFilteringTable(self, type):

		if type == self.__PLAYLIST_TYPE_ARTIST:
			return self.__ARTISTS_ALLOWED_FILTERS

		elif type == self.__PLAYLIST_TYPE_ALBUM:
			return self.__ALBUMS_ALLOWED_FILTERS

		elif type == self.__PLAYLIST_TYPE_GENRE:
			return self.__GENRES_ALLOWED_FILTERS

		elif type == self.__UNDEFINED_PLAYLIST_TYPE:
			return self.__UNDEFINED_ALLOWED_FILTERS

		elif type == self.__PLAYLIST_TYPE_ALL:
			return self.__ALL_ALLOWED_FILTERS

		return None


	def __addTrack(self, playlists, name, info, typ):
		playlistsExsists = False
		track = info['path']
		genre = info['genre']
		artist = info['artist']
		album = info['album']
		trackCover = info['cover']

		for index, playlist in enumerate(playlists):
			if playlist['name'] == name and playlist['type'] == typ:

				if playlist['cover'] == None and trackCover != None:
					playlist['cover'] = trackCover

				playlist['tracks'].append(track)

				if typ == self.__UNDEFINED_PLAYLIST_TYPE: #Add cover to tracks from undefined playlist
					playlist['tracks'][-1]['cover'] = trackCover

				playlistsExsists = True
				break

		if len(playlists) == 0 or not playlistsExsists:

			playlist = {
				"name" : name,
				"artist" : artist,
				"album" : album,
				"genre" : genre,
				"type" : typ,
				"cover" : trackCover,
				"tracks" : [track]
			}

			if typ == self.__UNDEFINED_PLAYLIST_TYPE: #Add cover to tracks from undefined playlist
				playlist['tracks'][-1]['cover'] = trackCover
		
			playlists.append(playlist)

		return playlists
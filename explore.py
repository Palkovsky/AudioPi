import os
import glob
import time
from constants import whitelisted_extensions, defaults, playlist_filters, limits, error_codes
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from helpers import send_error

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

	def getPathContent(self, path, metadata = False):

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
			if not metadata:
				files_list.append({
						"relative" : basename,
						"full" : f,
						"simple" : os.path.splitext(basename)[0]
				})
			else:
				files_list.append({
						"relative" : basename,
						"full" : f,
						"simple" : os.path.splitext(basename)[0],
						"metadata" : self.getMetadata(f)
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

	def getAllTracks(self, initialPath, sort = 1, simple = False, local = False):

		files_list = []
		startTime = int(round(time.time() * 1000))

		if not local:
			for dirpath, dirnames, filenames in os.walk(initialPath):
				for filename in [f for f in filenames if self.__isWhitelisted(f)]:
					fullPath = os.path.join(dirpath, filename)
					basename = os.path.basename(fullPath)

					f = self.__getFile(fullPath)
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

					endTime = int(round(time.time() * 1000))
					if endTime - startTime > limits.MAX_REQUEST_TIME * 1000:
						return send_error(error_codes.REQUEST_TIMEOUT, "Request took too much time", False)

		else:
			for fil in os.listdir(initialPath):
				if self.__isWhitelisted(fil):

					fullPath = os.path.join(initialPath, fil)

					f = self.__getFile(fullPath)
					if not simple:
						artist = f['artist'][0] if 'artist' in f else None
						album = f['album'][0] if 'album' in f else None
						genre = f['genre'][0] if 'genre' in f else None
						cover = self.__getCover(fullPath)
		
						files_list.append({
							"basename" : fil,
							"full" : fullPath,
							"simple" : os.path.splitext(fil)[0],
							"artist" : artist,
							"album" : album,
							"genre" : genre,
							"cover" : cover,
							"length" : round(f.info.length)
						})

					else:

						files_list.append({
							"basename" : fil,
							"full" : fullPath,
							"simple" : os.path.splitext(fil)[0],
							"length" : round(f.info.length)
						})


		return {
			"tracks" : self.__sortTracks(files_list, sort)
		}

	#Getting playlists via id3 tags
	def getAllPlaylists(self, initialPath, sort = 0, trackSort = 1, filt = [playlist_filters.NO_FILTERING], local = False):

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


		response = self.getAllTracks(initialPath, trackSort, True, local = local)
		if not 'code' in response:
			tracks = response['tracks']
		else:
			return response

		for track in tracks:
			path = track['full']
			f = self.__getFile(path)

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

		return {"playlists" : self.__sortPlaylists(playlists, sort)}

	def getMetadata(self, path):
		f = self.__getFile(path)
		artist = f['artist'][0] if 'artist' in f else None
		album = f['album'][0] if 'album' in f else None
		genre = f['genre'][0] if 'genre' in f else None

		response = {
			"path" : path,
 			"artist" : artist,
 			"album" : album,
 			"genre" : genre,
 			"length" : round(f.info.length),
 			"cover" : self.__getCover(path)
		}

		return response


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


		f = self.__getFile(path)
		artist = f['artist'][0] if 'artist' in f else None
		album = f['album'][0] if 'album' in f else None
		f = File(path)
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
					playlist['cover'] = None

				playlistsExsists = True
				break

		if len(playlists) == 0 or not playlistsExsists:

			if typ == self.__PLAYLIST_TYPE_GENRE:
				playlist = {
						"name" : name,
						"type" : typ,
						"cover" : trackCover,
						"tracks" : [track]
					}
			elif typ == self.__PLAYLIST_TYPE_ALBUM:
				playlist = {
						"name" : name,
						"artist" : artist,
						"genre" : genre,
						"type" : typ,
						"cover" : trackCover,
						"tracks" : [track]
					}
			else:
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
				playlist['cover'] = None
		
			playlists.append(playlist)

		return playlists

	def __sortTracks(self, tracks, method):
		if method == 1:
			return sorted(tracks, key = lambda k: k['simple'])
		elif method == 2:
			return sorted(tracks, key = lambda k: k['length'], reverse = True)
		elif method == 3:
			return sorted(tracks, key = lambda k: k['simple'], reverse = True)
		elif method == 4:
			return sorted(tracks, key = lambda k: k['length'])
		return tracks

	def __sortPlaylists(self, playlists, method):
		if method == 1:
			return sorted(playlists, key = lambda k: k['name'])
		elif method == 3:
			return sorted(playlists, key = lambda k: k['name'], reverse = True)
		return playlists

	def __getFile(self, path):
		extension = os.path.splitext(os.path.basename(path))[1]
		audio = None
		if(extension == ".mp3"):
			audio = MP3(path, ID3=EasyID3)
		elif(extension == ".flac"):
			audio = FLAC(path)
		elif(extension == ".ogg"):
			audio = OggVorbis(path)

		if audio != None:
			return audio
		return None
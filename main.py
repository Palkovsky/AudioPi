from playlist import Playlist
from track import Track
import threading
import os

tracks = ["tracks/track.mp3", "tracks/track2.mp3", "tracks/track3.flac", "tracks/track4.mp3"]
playlist = Playlist(tracks)
playlist.play(2)

while playlist.isPlaying() == True:

	if(playlist.currentTrack.getLength() <= playlist.currentTrack.getPlaybackPosition()):
		playlist.nextTrack()

	print(playlist.currentTrack.formattedTimestamp() +
	 "/" + playlist.currentTrack.formattedTimestamp(playlist.currentTrack.getLength()) +
	  " | " + playlist.currentTrack.getMetadata().get('title'))
	continue

playlist.dispose()

from playlist import Playlist
from track import Track
import threading
from queue import Queue
import os

playlist_lock = threading.Lock()
tracks = ["tracks/track.mp3", "tracks/track2.mp3", "tracks/track3.flac", "tracks/track4.mp3", "tracks/track5.mp3"]
playlist = Playlist(tracks)

def handle_input():
	while 1:
		cmd = input("cmd: ")
		if cmd == ">":
			with playlist_lock:
				playlist.nextTrack()
				print("playing: " + playlist.currentTrack.getMetadata().get('title'))
		elif cmd == "<":
			with playlist_lock:
				playlist.previousTrack()
				print("playing: " + playlist.currentTrack.getMetadata().get('title'))
		elif cmd == "+":
			playlist.setVolume(playlist.getVolume() + 0.1)
			print("Volume: " + str(playlist.getVolume()))
		elif cmd == "-":
			playlist.setVolume(playlist.getVolume() - 0.1)
			print("Volume: " + str(playlist.getVolume()))
		elif cmd == "p":
			if(playlist.isPaused()):
				playlist.unpause()
			else:
				playlist.pause()
				
def play_music():
	playlist.play()

	while playlist.isPlaying() == True:

		if(playlist.currentTrack.getLength() <= playlist.currentTrack.getPlaybackPosition()):
			playlist.nextTrack()

		print(playlist.currentTrack.formattedTimestamp() +
		 "/" + playlist.currentTrack.formattedTimestamp(playlist.currentTrack.getLength()) +
		  " | " + playlist.currentTrack.getMetadata().get('title'))
		continue

q = Queue()


inputThread = threading.Thread(target = handle_input)
inputThread.daemon = True
inputThread.start()

musicThread = threading.Thread(target = play_music)
musicThread.daemon = True
musicThread.start()

while 1:
	continue



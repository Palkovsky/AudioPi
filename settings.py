import json
import codecs

class Volumizer():

	def __init__(self):
		self.__path = 'settings/volume.json'

	def getJSON(self):
		with open(self.__path) as data_file:
			return json.load(data_file)

	def setVolume(self, vol):

		if vol == None:
			return None

		try:
			volume = float(vol)
		except:
			return None

		if volume < 0:
			return None
		if volume > 100:
			return None


		with open(self.__path, 'r') as f:
			json_data = json.load(f)
			json_data['config']['volume'] = volume
			json_data['config']['milli'] = volume / 100

		with open(self.__path, 'w') as f:
			f.write(json.dumps(json_data))



		return self.getJSON()

	def isMuted(self):
		with open(self.__path) as data_file:
			vol = json.load(data_file)['config']['milli']

		if vol == 0:
			return True
		return False

volumizer = Volumizer()

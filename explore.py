import os
import glob
from constants import whitelisted_extensions, defaults

class Explorer():

	def __init__(self):
		self.__default_path = defaults.path
		pass

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
				directories_list.append({ "directory" : {"relative" : directory,
														"full" : os.path.join(path, directory)}})

		files_list = []
		files = []

		for ext in whitelisted_extensions:
			files += glob.glob(path + '/*' + ext)

		for f in files:
			basename = os.path.basename(f)
			files_list.append({"file" : {
					"relative" : basename,
					"full" : f,
					"simple" : os.path.splitext(basename)[0]
		}})


		upDir = os.path.dirname(path)
		if path == self.__default_path:
			upDir = None


		return {
			"directory" : {
				"path" : path,
				"upDir" : upDir,
				"directories" : directories_list,
				"files" : files_list
			}
		}


	def __get_immediate_subdirectories(self, a_dir):
	    return [name for name in os.listdir(a_dir)
	            if os.path.isdir(os.path.join(a_dir, name))]

	def __path_leaf(self, path):
		if path.endswith('/'):
			return path[:-1]
		return path

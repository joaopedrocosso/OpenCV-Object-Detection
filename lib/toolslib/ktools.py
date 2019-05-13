import os

def get_files(path=None):
	'''Get all files from a path 'path'.

	Parameters:
		'path': (str) Path to files.
	'''
	
	if path is None:
		path = os.getcwd()
	files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	return files
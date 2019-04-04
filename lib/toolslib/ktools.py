import os

def get_files(path=None):
	
	if path is None:
		path = os.getcwd()
	files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	return files
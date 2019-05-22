import os

def get_files(path=None):
	'''Gets all files from a path 'path'.

	If no path is passed, the current directory is used.

	Parameters
	-----------
	path : str, optional
		Path to files. (Default: None)

	Returns
	--------
	list of str
		Files inside the directory 'path'.
	'''
	
	if path is None:
		path = os.getcwd()
	files = [os.path.join(path, f) for f in os.listdir(path)
			 if os.path.isfile(os.path.join(path, f))]
	return files
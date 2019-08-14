import os
import time

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

class LoopPeriodControl:
	'''
	Forces each iteration of a loop to take, at least, a set amount of 
	time to run.

	Parameters
	-----------
	loop_period : float
		Minimum amount of time an iteration must take to run. Must be 
		non-negative.
	
	Raises
	-------
	ValueError
		If an invalid value was provided to 'loop_period'.
	'''
	
	def __init__(self, loop_period):
		self.loop_period = loop_period
		self.start_time = time.time()
	
	def force_minimum_loop_period(self):
		time_since_start = time.time()-self.start_time
		if time_since_start <= self.loop_period:
			time.sleep(self.loop_period-time_since_start)
		self.start_time = time.time()	

	def reset(self):
		self.start_time = time.time()
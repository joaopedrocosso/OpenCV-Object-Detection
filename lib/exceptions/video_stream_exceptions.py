class VideoStreamError(Exception):
	
	def __init__(self, message, *args):

		super().__init__(message, *args)


class CannotOpenStreamError(VideoStreamError):
	pass

class StreamClosedError(VideoStreamError):
	pass	
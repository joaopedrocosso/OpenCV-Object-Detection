from webcamVideoStream import WebcamVideoStream

class VideoStream:
	def __init__(self,source=0,usePiCamera=False,resolution=(320,240),framerate=32):
		if usePiCamera:
			from piVideoStream import PiVideoStream
			self.stream = PiVideoStream(resolution = resolution,framerate = framerate)
		else:
			self.stream = WebcamVideoStream(src=source)

	def start(self):
		return self.stream.start()

	def update(self):
		self.stream.update()

	def read(Self):
		return self.stream.read()

	def stop(self):
		self.stream.stop()
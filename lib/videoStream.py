from webcamVideoStream import WebcamVideoStream
from ipVideoStream import IPVideoStream

class VideoStream:
	def __init__(self,source=0,cameraType="webcam",resolution=(320,240),framerate=32,url="algumip",login="teste",password="teste"):
		if cameraType == "picamera" :
			from piVideoStream import PiVideoStream
			self.stream = PiVideoStream(resolution = resolution,framerate = framerate)
		elif cameraType == "ipcamera":
			self.stream = IPVideoStream(url,login,password)
		else:
			self.stream = WebcamVideoStream(src=source)

	def start(self):
		return self.stream.start()

	def update(self):
		self.stream.update()

	def read(self):
		return self.stream.read()

	def stop(self):
		self.stream.stop()
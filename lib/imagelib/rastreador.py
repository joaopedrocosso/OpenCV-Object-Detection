import cv2 as cv

class Rastreador:
	'''TODO'''

	def __init__(self, tipo_rastreador='kcf'):
		self.rastreador = cv.MultiTracker_create()
		self.tipo_rastreador = tipo_rastreador


OPENCV_OBJECT_TRACKERS = {
	'csrt': cv.TrackerCSRT_create,
	'kcf': cv.TrackerKCF_create,
	'boosting': cv.TrackerBoosting_create,
	'mil': cv.TrackerMIL_create,
	'tld': cv.TrackerTLD_create,
	'medianflow': cv.TrackerMedianFlow_create,
	'mosse': cv.TrackerMOSSE_create
}
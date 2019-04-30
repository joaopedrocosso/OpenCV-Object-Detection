import cv2 as cv
import numpy as np

def black_image(width, height, image_type='bgr'):

	''' Returns a black image of dimensions (width x height) and of type 'image_type'.
	
	width, height: integers
	image_type: string
	'''
	
	try:
		width = int(width)
		height = int(height)
	except TypeError:
		raise TypeError('Width and height must be integers')
		
	if not isinstance(image_type, str):
		raise TypeError('Image type must be a string')

	if image_type == 'bgr' or image_type == 'rgb' or image_type == 'hsv':
		return np.zeros((height, width, 3), np.uint8)
	elif image_type == 'grayscale':
		return np.zeros((height, width), np.uint8)
	
	raise ValueError('Unknown image type: "{}"'.format(image_type))


def show_image(img, title='title', wait_time=0, close_window=True):

	''' Opens window with the desired image '''

	if (not isinstance(img, np.ndarray) or not isinstance(title, str)
		or not isinstance(wait_time, int) or not isinstance(close_window, bool)):

		raise TypeError("'img' must be of type 'numpy.ndarray'; 'title', of type 'str';"+
						"'wait_time' of type 'int' and; 'close_window' of type 'bool'")

	cv.imshow(title, img)
	k = cv.waitKey(wait_time) & 0xFF
	if close_window:
		cv.destroyWindow(title)
	return k


def resize(img, new_width=None, new_height=None):

	''' Resizes image to the desired size. If only one of the dimensions
	is specified, the image is resized proportionally.'''

	if new_width is None and new_height is None:
		raise ValueError('At least one dimension must be provided.')
	if not isinstance(img, np.ndarray):
		raise TypeError("'img' variable must be of type numpy.ndarray.") 

	old_height, old_width = img.shape[:2]

	def check_positive_dimension(dimension, name):
		try:
			dimension = float(dimension)
		except ValueError:
			raise TypeError("'{}' must be float or int.".format(name))
		if dimension <= 0:
			raise ValueError("'{}' must be positive.".format(name))
		return dimension

	if new_width is not None:
		new_width = check_positive_dimension(new_width, 'new_width')
	if new_height is not None:
		new_height = check_positive_dimension(new_height, 'new_height')


	if new_width is not None and new_height is not None:
		pass

	elif new_width is not None:
		new_height = float(old_height)*new_width/old_width

	elif new_height is not None:
		new_width = float(old_width)*new_height/old_height
	
	new_img = cv.resize(img, (int(new_width), int(new_height)))
	return new_img


def draw_rectangles(image, rectangles_and_info, overwrite_original=False, write_weight=True):

	'''Draw rectangles on an image'''

	if not overwrite_original:
		image = image.copy()

	# Draws each rectangle with its related info, if available.
	for rectangle, info in rectangles_and_info:

		# extract coordenates
		(x, y) = rectangle[:2]
		(w, h) = rectangle[2:4]
 
		# Draws rectangle and text.
		cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0xFF), 2)
		if write_weight:
			text = "{:.4f}".format(info)
			cv.putText(image, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0xFF, 0xFF, 0xFF), 2)

	return image

def non_maxima_suppression(caixas, precisoes, precisao_minima, supressao_caixas):

	idxs = cv.dnn.NMSBoxes(caixas, precisoes, precisao_minima, supressao_caixas)
	if not isinstance(idxs, np.ndarray):
		idxs = np.array([])
	return idxs.flatten()


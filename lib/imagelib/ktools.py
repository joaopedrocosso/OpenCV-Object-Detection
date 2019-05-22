import cv2 as cv
import numpy as np

def black_image(width, height, image_type='bgr'):

	'''Returns a black image.
	
	Parameters
	-----------
	width, height: int
		Width and height of the image.
	image_type: {'bgr', 'rgb', 'hsv', 'grayscale'}, optional
		Format of the image.

	Returns
	--------
	numpy.ndarray
		Multi-dimensional array of shape adequate for the type provided.

	Raises
	-------
	ValueError
		If 'image_type' is an invalid type.
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
	'''Opens a window with the desired image.

	Returns control after 'wait_time' seconds or after the user presses
	a key on the keyboard.

	Parameters
	-----------
	img : numpy.ndarray
		Image to be shown on the window box.
	title : str, optional
		Title of the window. Default='title'.
	wait_time : int, optional
		Time to wait before returning control to the program.
		If it equals 0, then it won't be closed. Default=0.
	close_window : bool, optional
		If True, the window will be closed after control is returned.

	Returns
	--------
	int
		Key pressed on the window.

	Raises
	-------
	TypeError
		If any arguments have the wrong type.
	'''

	if (not isinstance(img, np.ndarray) or not isinstance(title, str)
		or not isinstance(wait_time, int) or not isinstance(close_window, bool)):
		#
		raise TypeError(
			"'img' must be of type 'numpy.ndarray';\n"
			"'title', of type 'str';\n"
			"'wait_time' of type 'int';\n"
			"'close_window' of type 'bool'.")

	cv.imshow(title, img)
	k = cv.waitKey(wait_time) & 0xFF
	if close_window:
		cv.destroyWindow(title)
	return k


def resize(img, new_width=None, new_height=None):
	'''Resizes image to the desired size.

	If only one of the dimensions is specified, the image is resized 
	proportionally. 

	Parameters
	-----------
	img : numpy.ndarray
		The image to be resized.
	new_width : int, optional
		The new width of the image. (> 0)
	new_height : int, optional
		The new height of the image. (> 0)
	
	Raises
	------
	ValueError
		If no arguments are given.

	Returns
	--------
	numpy.ndarray
		The resized image.
	'''

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


def draw_rectangles(image, rectangles_and_info, overwrite_original=False,
					write_weight=True):
	'''Draw rectangles on an image
	
	Parameters
	-----------
	image : numpy.ndarray
		The image on which the retangles will be drawn.
	rectangles_and_info : [((int, int, int, int), float), ...]
		The coordinates and dimensions of a rectangle, plus information
		about it.
	overwrite_original : bool, optional
		If true, the rectangles are drawn on the original image.
		Otherwise they are drawn on a copy.
	write_weight : bool, optional
		If true, the info in 'rectangles_and_info' is written on the
		image.

	Returns
	--------
	numpy.ndarray
		Image on which the rectangles were drawn.
	'''

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

def non_maxima_suppression(caixas, precisoes, precisao_minima=0.5,
						   supressao_caixas=0.4):
	'''Combina caixas muito próximas ou dentro de outras.

	Parameters
	-----------
	caixas : [(int, int, int, int), ...]
		Caixas com as coordenadas x, y e suas dimensões.
	precisoes : list of float
		Precisões de cada uma das caixas.
	precisao_minima : float
		Precisão mínima para a caixa ser aceita.
		(0.0 <= 'precisao_minima' <= 1.0) e (Padrão=0.5)
	supressao_caixas : float
		Nível de supressão das caixas.
		(0.0 <= 'supressao_caixas' <= 1.0) e Padrão=0.4)

	Returns
	--------
	numpy.ndarray
		Índices das caixas resultantes.
	'''

	idxs = cv.dnn.NMSBoxes(caixas, precisoes, precisao_minima, supressao_caixas)

	# cv.dnn.NMSBoxes retorna uma tupla, se não houver caixas resultantes.
	if not isinstance(idxs, np.ndarray):
		idxs = np.array([])
	return idxs.flatten()


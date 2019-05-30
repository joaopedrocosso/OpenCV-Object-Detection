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

def destroy_all_windows():
	'''Destroys all windows created using opencv.'''
	cv.destroyAllWindows()


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


def draw_boxes(image, boxes, infos=[], overwrite_original=False,
			   write_infos=True):
	'''Draw boxes on an image.
	
	Parameters
	-----------
	image : numpy.ndarray
		The image on which the boxes will be drawn.
	boxes : [(int, int, int, int), ...]
		Boxes that will be drawn on the image.
	infos : [str, ...], optional
		Information about each box, that will be displayed above 
		them. Values can be of any class as long as they can be 
		converted to strings. If not provided, nothing will be written. 
		If there are less elements in 'infos' than there are in 'boxes', 
		nothing will be displayed on top of the remaining boxes.
	overwrite_original : bool, optional
		If true, the rectangles are drawn on the original image.
		Otherwise they are drawn on a copy.
	write_infos : bool, optional
		If true, the info in 'infos' will be written on the image.

	Returns
	--------
	numpy.ndarray
		Image on which the rectangles were drawn.
	'''

	if not overwrite_original:
		image = image.copy()
	# Make sure 'infos' has at least the same length as 'boxes'
	infos.extend(['']*(len(boxes)-len(infos)))

	# Draws each rectangle with its related info, if available.
	for rectangle, info in zip(boxes, infos):

		# extract coordenates
		(x, y) = rectangle[:2]
		(w, h) = rectangle[2:4]
 
		# Draws rectangle and text.
		cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0xFF), 2)
		if write_infos:
			write(image, info, x=x, y=y-5, font_scale=0.5)

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


def write(image, text, x, y, font=cv.FONT_HERSHEY_SIMPLEX, font_scale=0.8,
		  color=(0xFF, 0xFF, 0xFF), thickness=2, outline=False,
		  outline_color=(0x00, 0x00, 0x00)):
	'''Convinience function to write text on an image.
	
	Parameters
	-----------
	image : numpy.ndarray
		Image to write on.
	text : str
		Text to be written on the image.
	x, y : int
		Coordinates of the bottom-left corner of the text.
	font : int, optional
		Constants to the opencv fonts. For all options, check their
		documentation. (Default=cv.FONT_HERSHEY_SIMPLEX)
	font_scale : float, optional
		Factor that is multiplied by the font-specific base size.
		(Default=0.5)
	color : tuple of int, optional
		RGB color of the text. (Default=(0xFF, 0xFF, 0xFF))
	thickness : int, optional
		Thickness of the text. (Default=2)
	outline : bool, optional
		If set to true, the text will be outlined. (Default=False)
	outline_color : tuple of int, optional
		Color of the outline. (Default=(0x00, 0x00, 0x00))
	'''
	if outline:
		cv.putText(image, text, (x, y), font, font_scale, outline_color, thickness+5)
	cv.putText(image, text, (x, y), font, font_scale, color, thickness)
	
from imagelib import ktools
from videolib.webcamVideoStream import WebcamVideoStream
from imagelib.detector_objetos.detector_objetos_yolo import DetectorObjetosYolo

detector = DetectorObjetosYolo('../detector-itens/modelo-yolo/')
vs = WebcamVideoStream().start()

while not vs.stopped:
	img = vs.read()
	caixas_precisoes_rotulos = detector.detectar(img)
	if 'person' in caixas_precisoes_rotulos:
		caixas, precisoes = caixas_precisoes_rotulos['person']
		nova_img = ktools.draw_boxes(img, caixas, precisoes)
	else:
		nova_img = img
	ktools.show_image(nova_img, title='Detector', wait_time=1, close_window=False)

vs.stop()
ktools.destroy_all_windows()

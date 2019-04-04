from enum import Enum

class Entrada(Enum):

	WEBCAM = 0
	IPCAMERA = 1
	PICAMERA = 2
	ARQUIVO = 3

	@classmethod
	def confere_valor(cls, valor):
		return any(valor == item.value for item in cls)

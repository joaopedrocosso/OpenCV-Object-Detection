'''Módulo de funções auxiliares para os leitores de vídeo.'''


def adiciona_autenticacao_url(url, login, senha):

	'''Retorna uma url no formato porta://login:senha@endereço.

	Parâmetros
	----------
	url : str
		URL ou endereço ip desejado.
	login : str
		Login.
	senha : str
		Senha.

	Retorna
	--------
	str
		Endereço final.
	'''

	# Separa url da porta, se houver.
	if '//' in url:
		porta, endereco = url.split('//')
		porta += '//'
	else:
		porta, endereco = '//', url

	endereco_final = '{}{}:{}@{}'.format(porta, login, senha, endereco)
	return endereco_final

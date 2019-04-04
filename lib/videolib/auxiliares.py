
def adiciona_autenticacao_url(url, login, senha):

	'''Retorna uma url no formato porta://login:senha@endereco'''

	# Separa url da porta, se houver.
	if '//' in url:
		porta, endereco = url.split('//')
		porta += '//'
	else:
		porta, endereco = '//', url

	endereco_final = '{}{}:{}@{}'.format(porta, login, senha, endereco)
	return endereco_final

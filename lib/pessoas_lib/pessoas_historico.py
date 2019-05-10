import time
from collections import deque

class PessoasHistorico:

    _DEFAULT_MAX_HISTORICO = 20
    def __init__(self, max_historico=_DEFAULT_MAX_HISTORICO):

        if not isinstance(max_historico, int) or max_historico <= 0:
            max_historico = PessoasHistorico._DEFAULT_MAX_HISTORICO

        self.historico = deque(maxlen=max_historico)
        self.pessoa_atual = PessoasEmPeriodo()
        self.min_todos = float('inf')
        self.max_todos = float('-inf')

    def atualiza_pessoa(self, valor):
        self.pessoa_atual.atualiza(valor)
        return self

    def checa_tempo_decorrido(self, tempo_limite):
        return self.pessoa_atual.tempo_decorrido >= tempo_limite

    def finaliza_pessoa(self):

        media, max_atual, min_atual, tempo_decorrido = self.pessoa_atual.pega_valor_final()

        if self.max_todos < max_atual:
            self.max_todos = max_atual
        if self.min_todos > min_atual:
            self.min_todos = min_atual

        self.pessoa_atual = PessoasEmPeriodo()
        self.historico.append((media, max_atual, min_atual, tempo_decorrido))
        return self.historico[-1]

    def __str__(self):

        if len(self.historico) > 0:
            ultimo_maximo, ultimo_minimo = self.historico[-1][1:3]
            minimo_todos, maximo_todos = self.min_todos, self.max_todos
        else:
            ultimo_maximo = ultimo_minimo = minimo_todos = maximo_todos = 'N/D'

        return ('Último mínimo: {}\n'
                'Último máximo: {}\n'
                'Mínimo desde o início: {}\n'
                'Máximo desde o início: {}'
                .format(ultimo_minimo, ultimo_maximo, minimo_todos, maximo_todos)
        )


class PessoasEmPeriodo:

    def __init__(self):

        self.pessoas = []
        self.tempo_decorrido = 0.0
        self.ultimo_tempo = time.time()

    def atualiza(self, valor):

        tempo_desde_ultima_atualizacao = time.time()-self.ultimo_tempo
        self.pessoas.append((valor, tempo_desde_ultima_atualizacao))

        self.tempo_decorrido += tempo_desde_ultima_atualizacao
        self.ultimo_tempo = time.time()

    def pega_valor_final(self):

        if self.tempo_decorrido <= 0:
            return 0, 0, 0, 0

        media = sum(valor*tempo for valor, tempo in self.pessoas)/self.tempo_decorrido
        min_valor = min(self.pessoas, key=lambda x: x[0])[0]
        max_valor = max(self.pessoas, key=lambda x: x[0])[0]
        
        return round(media), max_valor, min_valor, self.tempo_decorrido
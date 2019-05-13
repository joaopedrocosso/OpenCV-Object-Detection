import time
from collections import deque

class PessoasHistorico:

    def __init__(self, max_historico=20):
        '''Grava estatísticas de pessoas em um período de tempo.
        
        Parâmetros:
            'max_historico': (int) Máximo de iterações guardadas.

        Levanta:
            ValueError: Se max_historico não for 'int' ou for <= 0.
        '''

        if not isinstance(max_historico, int) or max_historico <= 0:
            raise ValueError("'max_historico' deve ser um inteiro não-negativo.")

        self.historico = deque(maxlen=max_historico)
        self.pessoa_atual = PessoasEmPeriodo()
        self.min_todos = float('inf')
        self.max_todos = float('-inf')

    def atualiza_pessoa(self, valor):
        '''Adiciona valores para a iteração atual.

        Parâmetros:
            'valor': (float) valor a ser adicionado.
        '''
        self.pessoa_atual.atualiza(valor)
        return self

    def checa_tempo_decorrido(self, tempo_limite):
        '''Checa se o tempo decorrido passou do limite.'''
        return self.pessoa_atual.tempo_decorrido >= tempo_limite

    def finaliza_pessoa(self):
        '''Pega dados da iteração atual e inicia uma nova.
        
        Retorno:
            1. Média ponderada dos valores com o intervalo de tempo.
            2. Valor máximo recebido.
            3. Valor mínimo recebido.
            4. Tempo total decorrido.
            (tudo somente da iteração atual.)
        '''

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
        '''Guarda o número de pessoas por período de tempo.'''

        self.pessoas = []
        self.tempo_decorrido = 0.0
        self.ultimo_tempo = time.time()

    def atualiza(self, valor):
        '''Adiciona um novo valor com o tempo desde a últma atualização (ou criação).

        Parâmetros:
            'valor': (float) valor a ser adicionado.
        '''

        tempo_desde_ultima_atualizacao = time.time()-self.ultimo_tempo
        self.pessoas.append((valor, tempo_desde_ultima_atualizacao))

        self.tempo_decorrido += tempo_desde_ultima_atualizacao
        self.ultimo_tempo = time.time()

    def pega_valor_final(self):
        '''Retorna valores relacionados aos valores registrados.
        
        Retorno:
            1. Média ponderada dos valores com o intervalo de tempo.
            2. Valor máximo recebido.
            3. Valor mínimo recebido.
            4. Tempo total decorrido.
        '''

        if self.tempo_decorrido <= 0 or len(self.pessoas) == 0:
            return 0, 0, 0, 0

        media = sum(valor*tempo for valor, tempo in self.pessoas)/self.tempo_decorrido
        min_valor = min(self.pessoas, key=lambda x: x[0])[0]
        max_valor = max(self.pessoas, key=lambda x: x[0])[0]
        
        return round(media), max_valor, min_valor, self.tempo_decorrido
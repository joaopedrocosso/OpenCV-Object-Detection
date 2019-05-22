import time
from collections import deque

class PessoasHistorico:

    '''Grava estatísticas de pessoas em um período de tempo.

    Cada período é considerado uma iteração e os resultados de cada
    iteração, finalizadas em 'finaliza_pessoa()', são guardados em
    um históricod de capacidade 'max_historico'.
    
    Parameters
    -----------
    max_historico : int, optional
        Máximo de iterações guardadas. (Padrão=20)
    tempo_limite : float, optional
        Tempo máximo. (Padrão=inf)

    Raises
    --------
    ValueError
        Se max_historico não for 'int' ou for menor que zero
    '''

    def __init__(self, max_historico=20, tempo_limite=float('inf')):

        if not isinstance(max_historico, int) or max_historico <= 0:
            raise ValueError("'max_historico' deve ser um inteiro não-negativo.")

        self.historico = deque(maxlen=max_historico)
        self.pessoa_atual = PessoasEmPeriodo()
        self.min_todos = float('inf')
        self.max_todos = float('-inf')

    def atualiza_pessoa(self, valor):
        '''Adiciona valores para a iteração atual.

        Parameters
        -----------
        valor : float
            Valor a ser adicionado.

        Returns
        --------
        self
        '''
        self.pessoa_atual.atualiza(valor)
        return self

    def pega_tempo_decorrido(self):
        '''Retorna o tempo decorrido desde que a iteração atual começou.

        Returns
        --------
        float
            Tempo decorrido.
        '''
        return self.pessoa_atual.tempo_decorrido

    def finaliza_pessoa(self):
        '''Pega dados da iteração atual e inicia uma nova.

        Os valores de retorno se referem apenas à iteração atual.
        
        Returns
        --------
        media : float
            Média ponderada dos valores com o intervalo de tempo.
        max_valor : float
            Valor máximo recebido.
        min_valor : float
            Valor mínimo recebido.
        tempo_decorrido : float
            Tempo total decorrido.
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

        '''Retorna uma string que representa o objeto.

        Returns
        --------
        str
            Os valores máximo e mínimo da última iteração e os valores
            máximo e mínimo desde a instanciação do objeto.
        '''

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
        '''Guarda o número de pessoas por período de tempo.

        Também guarda o tempo decorrido desde a instanciação.'''

        self.pessoas = []
        self.tempo_decorrido = 0.0
        self.ultimo_tempo = time.time()

    def atualiza(self, valor):
        '''Adiciona um novo valor com o tempo desde a últma atualização (ou criação).

        Parameters
        -----------
        valor : int
            Valor a ser adicionado. Deve ser não negativo.
        '''

        if valor < 0:
            raise ValueError('Valor deve ser um inteiro não negativo.')

        tempo_desde_ultima_atualizacao = time.time()-self.ultimo_tempo
        self.pessoas.append((valor, tempo_desde_ultima_atualizacao))

        self.tempo_decorrido += tempo_desde_ultima_atualizacao
        self.ultimo_tempo = time.time()

    def pega_valor_final(self):
        '''Retorna valores relacionados aos valores registrados.
        
        Returns
        --------
        media : float
            Média ponderada dos valores com o intervalo de tempo.
        max_valor : float
            Valor máximo recebido.
        min_valor : float
            Valor mínimo recebido.
        tempo_decorrido : float
            Tempo total decorrido.
        '''

        if self.tempo_decorrido <= 0 or len(self.pessoas) == 0:
            return 0, 0, 0, 0

        media = sum(valor*tempo for valor, tempo in self.pessoas)/self.tempo_decorrido
        min_valor = min(self.pessoas, key=lambda x: x[0])[0]
        max_valor = max(self.pessoas, key=lambda x: x[0])[0]
        
        return round(media), max_valor, min_valor, self.tempo_decorrido
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

    Raises
    --------
    ValueError
        Se max_historico não for 'int' ou for menor que zero
    '''

    def __init__(self, max_historico=20):

        if not isinstance(max_historico, int) or max_historico <= 0:
            raise ValueError("'max_historico' deve ser um inteiro não-negativo.")

        self._inicia_novo_periodo()
        self.historico = deque(maxlen=max_historico)
        self.min_todos = float('inf')
        self.max_todos = float('-inf')

    def _inicia_novo_periodo(self):
        self.min_atual = float('inf')
        self.max_atual = float('-inf')
        self.soma_ponderada = 0
        self.tempo_decorrido = 0
        self.ultimo_tempo = time.time()


    def atualiza_periodo(self, valor):
        '''Adiciona valores para a iteração atual.

        Parameters
        -----------
        valor : float
            Valor a ser adicionado.

        Returns
        --------
        self
        '''
        if self.min_atual > valor:
            self.min_atual = valor
            if self.min_todos > valor:
                self.min_todos = valor
        if self.max_atual < valor:
            self.max_atual = valor
            if self.max_todos < valor:
                self.max_todos = valor

        tempo = time.time()-self.ultimo_tempo
        self.soma_ponderada += valor*tempo
        self.tempo_decorrido += tempo
        self.ultimo_tempo += tempo
        
        return self

    def pega_tempo_decorrido(self):
        '''Retorna o tempo decorrido desde que a iteração atual começou.

        Returns
        --------
        float
            Tempo decorrido.
        '''
        return self.tempo_decorrido

    def finaliza_periodo(self):
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
        if self.tempo_decorrido != 0:
            media = self.soma_ponderada/self.tempo_decorrido
        else:
            media = 0.0
        self.historico.append((media, self.max_atual, self.min_atual,
                               self.tempo_decorrido))
        self._inicia_novo_periodo()
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
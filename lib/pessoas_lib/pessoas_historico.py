import time
from collections import deque

class PessoasHistorico:

    _DEFAULT_MAX_HISTORICO = 20
    def __init__(self, max_historico=_DEFAULT_MAX_HISTORICO):

        if not isinstance(max_historico, int) or max_historico <= 0:
            max_historico = PessoasHistorico._DEFAULT_MAX_HISTORICO

        self.historico = deque(maxlen=max_historico)
        self.pessoa_atual = PessoasEmPeriodo()

    def atualiza_pessoa(self, valor):

        self.pessoa_atual.atualiza(valor)
        return self

    def checa_tempo_decorrido(self, tempo_limite):

        return self.pessoa_atual.tempo_decorrido >= tempo_limite

    def finaliza_pessoa(self):

        self.historico.append(self.pessoa_atual)
        self.pessoa_atual = PessoasEmPeriodo()
        return self.historico[-1].pegaValorFinal()


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

    def pegaValorFinal(self):

        self.pessoas.sort(key=lambda x: x[0])

        if self.tempo_decorrido <= 0:
            return 0, 0, 0, 0

        media = sum(valor*tempo for valor, tempo in self.pessoas)/self.tempo_decorrido
        minValor = self.pessoas[0][0]
        maxValor = self.pessoas[-1][0]
        
        return round(media), maxValor, minValor, self.tempo_decorrido
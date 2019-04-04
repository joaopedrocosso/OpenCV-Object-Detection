import math

from .pessoa import Pessoa

class Pessoas:

    def __init__(self, tempoConfirmarPessoa=1, tempoMaximoDeVidaPessoa=10, precisaoMinima=0.5):

        # self.pessoas, self.idContador, self.pessoasConfirmadas
        self.reiniciar()
    
        try:
            self.precisaoMinima = int(precisaoMinima)
            self.tempoConfirmarPessoa = int(tempoConfirmarPessoa)
            self.tempoMaximoDeVidaPessoa = float(tempoMaximoDeVidaPessoa)
        except ValueError:
            raise ValueError(
                "'tempoConfirmarPessoa' e 'tempoMaximoDeVidaPessoa' devem ser numeros inteiros e"
                "'precisaoMinima' deve ser um numero real.")
            
        if (self.precisaoMinima < 0.0 or self.precisaoMinima > 1.0 or
            not self.tempoMaximoDeVidaPessoa > self.tempoConfirmarPessoa > 0):
                raise ValueError(
                    "Valores devem ser 'tempoMaximoDeVidaPessoa'"
                    " > 'tempoConfirmarPessoa' > 0 e 0.0 <= 'precisaoMinima' <= 1.0.")


    def reiniciar(self):

        self.pessoas = []
        self.idContador = 0
        self.pessoasConfirmadas = 0


    def pegaNumeroPessoas(self):
        return len(self.pessoas)


    def atualizar(self, caixasComPeso):

        '''Atualiza lista de pessoas.'''

        self._verificarIdadeDasPessoas()
        return self._processarCaixas(caixasComPeso)


    def _verificarIdadeDasPessoas(self):

        '''Atualiza os contadores e envelhece as pessoas da lista.'''

        # Verificando/incrementando a idade as pessoas
        for p in self.pessoas:
            p.envelhece()
            if not p.isViva():
                indice = self.pessoas.index(p)
                self.pessoas.pop(indice)

        nPessoasNovo = 0
        for p in self.pessoas:
            if p.isConfirmada():
                nPessoasNovo+=1
        self.pessoasConfirmadas = nPessoasNovo

        return self.pessoasConfirmadas


    def _processarCaixas(self, caixasComPeso):
        
        '''Verificar nas caixas encontradas, se alguma pessoa eh nova/velha e atualizar dados.'''

        # Adaptando as coordenadas do array para guarda-lo no objeto pessoa
        # para cada objeto detectado em caixas:
        
        caixasConfirmadas = []

        for (startX,startY, w, h), peso in caixasComPeso:
            
            if peso < self.precisaoMinima:
                continue
            cx = startX + w//2
            cy = startY + h//2

            # Checando se o novo objeto ja existe ou esta proximo de uma pessoa
            for p in self.pessoas:
                # Se esta muito perto, ele nao eh novo. Ele eh uma pessoa que andou
                if (abs(cx-p.x)<=w and abs(cy-p.y)<=h):
                    # Atualiza a lista de posicoes da pessoa, incrementa o
                    # numero de frames que apareceu e reseta a idade
                    p.atualiza(cx,cy, w, h, peso)
                    break
            # Se eh novo, entao criar nova pessoa
            # e atualizar o contador de chaves(IDs)
            else:
                p = Pessoa(self.idContador, cx, cy, w, h, peso, self.tempoConfirmarPessoa, self.tempoMaximoDeVidaPessoa)
                self.pessoas.append(p)
                self.idContador += 1

        return [[(p.x - p.w//2, p.y - p.h//2, p.w, p.h), p.peso] for p in self.pessoas if p.isConfirmada()]


    def __str__(self):

        ret = ''
        for p in self.pessoas:
            ret += str(p) + '\n'
        return ret
import math

from .pessoa import Pessoa

class Pessoas:

    def __init__(self, minFramesParaConfirmar=1, maxTempoDesaparecida=10, precisaoMinima=0.5):

        # self.pessoas, self.idContador, self.pessoasConfirmadas
        self.reiniciar()
    
        try:
            self.precisaoMinima = int(precisaoMinima)
            self.minFramesParaConfirmar = int(minFramesParaConfirmar)
            self.maxTempoDesaparecida = float(maxTempoDesaparecida)
        except ValueError:
            raise ValueError(
                "'minFramesParaConfirmar' e 'maxTempoDesaparecida' devem ser numeros inteiros e"
                "'precisaoMinima' deve ser um numero real.")
            
        if (self.precisaoMinima < 0.0 or self.precisaoMinima > 1.0 or
            not self.maxTempoDesaparecida > self.minFramesParaConfirmar > 0):
                raise ValueError(
                    "Valores devem ser 'maxTempoDesaparecida'"
                    " > 'minFramesParaConfirmar' > 0 e 0.0 <= 'precisaoMinima' <= 1.0.")


    def reiniciar(self):

        self.pessoas = {}
        self.idContador = 0
        self.pessoasConfirmadas = 0


    def pegaNumeroPessoas(self):
        return len(self.pessoas)


    def atualizar(self, caixasComPeso):

        '''Atualiza lista de pessoas.'''

        self._atualizaPessoasDesaparecidas()

        if len(caixasComPeso) == 0:
            return self.getPessoas(pos='cima-esquerda')

        if len(self.pessoas) == 0:
            self.reiniciar()
            for (x, y, w, h), peso in caixasComPeso:
                cx = x - w//2
                cy = y - h//2
                self._registra_pessoa(cx, cy, w, h, peso)
            return self.getPessoas(pos='cima-esquerda')





    def getCaixasPessoas(self, pos='centro'):

        '''Retorna as caixas equivalentes 'as pessoas, com peso.

        Retorno e' uma lista de tuplas [((x, y, w, h), peso), ...]

        Parametros:
            pos: posicao que a coordenada (x, y) representa. Pode ser:
                'centro', (padrao)
                'cima',
                'baixo',
                'direita',
                'esquerda',
                'cima-esquerda'
                'cima-direita',
                'baixo-esquerda',
                'baixo-direita'.
         '''

        pessoasRetorno = []
        for pessoa in self.pessoas:

            (x, y, w, h), peso = pessoa.getCaixaComPeso()

            if pos in ['esquerda', 'cima-esquerda', 'baixo-esquerda']:
                x -= w//2
            elif pos in ['direita', 'cima-direita', 'baixo-direita']:
                x += w//2

            if pos_y in ['cima', 'cima-esquerda', 'cima-direita']:
                y -= h//2
            elif pos_y in ['baixo', 'baixo-esquerda', 'baixo-direita']:
                y += h//2

            pessoasRetorno.append( ((x, y, w, h), peso) )

        return pessoasRetorno


    def _atualizaPessoasDesaparecidas(self):

        '''
        Atualiza o numero de pessoas confirmadas e ha quanto
        tempo cada pessoa esta desaparecida.
        '''

        for p in self.pessoas:
            p.aumentaTempoDesaparecida()
            if not p.isViva():
                indice = self.pessoas.index(p)
                self.pessoas.pop(indice)

        nPessoasNovo = 0
        for p in self.pessoas:
            if p.isConfirmada():
                nPessoasNovo+=1
        self.pessoasConfirmadas = nPessoasNovo

        return self.pessoasConfirmadas

    
    def _registra_pessoa(self, x, y, w, h, peso):

        self.pessoas[self.idContador] = Pessoa(
            x, y, w, h, peso, self.minFramesParaConfirmar, self.maxTempoDesaparecida
        )
        self.idContador += 1




    '''def _processarCaixas(self, caixasComPeso):
        
        #Verificar nas caixas encontradas, se alguma pessoa eh nova/velha e atualizar dados.

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

        return [[(p.x - p.w//2, p.y - p.h//2, p.w, p.h), p.peso] for p in self.pessoas if p.isConfirmada()]'''




    def __str__(self):

        ret = ''

        chave = self.pessoas.keys()
        for chave in chaves:
            ret += str(chave) + ': ' + str(self.pessoas[chave]) + '\n'
        return ret
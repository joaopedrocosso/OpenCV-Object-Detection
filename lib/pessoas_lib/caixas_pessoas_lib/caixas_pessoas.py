# -*- coding: utf-8 -*-

from scipy.spatial import distance

from .caixa_pessoa import CaixaPessoa
from imagelib import caixa_tools

class CaixasPessoas:

    def __init__(self, min_frames_para_confirmar=1, max_tempo_desaparecida=10, precisao_minima=0.0):

        # self.pessoas, self.id_contador, self.pessoas_confirmadas
        self.reiniciar()
    
        # Levanta ValueError. Checa max_tempo_desaparecida e precisao_minima.
        CaixaPessoa(100, 100, 1, 1, None, min_frames_para_confirmar, max_tempo_desaparecida)
        self.min_frames_para_confirmar = int(min_frames_para_confirmar)
        self.max_tempo_desaparecida = int(max_tempo_desaparecida)

        try:
            self.precisao_minima = float(precisao_minima)
            if not 0.0 <= self.precisao_minima <= 1.0:
                raise ValueError
        except ValueError:
            raise ValueError("'precisao_minima' deve ser um número real entre 0.0 e 1.0 inclusive.")


    def reiniciar(self):
        self.pessoas = {}
        self.id_contador = 0
        self.pessoas_confirmadas = 0


    def atualizar(self, caixas_com_peso, pos_original='cima-esquerda'):

        '''Atualiza lista de pessoas.'''

        self._atualiza_pessoas_desaparecidas()

        # Só usa as caixas com precisão >= precisão mínima.
        if self.precisao_minima > 0.0:
            caixas_com_peso = [c for c in caixas_com_peso if c[1] >= self.precisao_minima]

        if len(caixas_com_peso) == 0:
            pass

        elif len(self.pessoas) == 0:
            self.reiniciar()
            self._registra_pessoas(caixas_com_peso, pos_original=pos_original)

        else:
            pessoas_ids = list(self.pessoas.keys())
            pessoas_centroides = [p.pega_coordenadas() for p in self.pessoas.values()]

            distancias = distance.cdist(pessoas_centroides, [c[:2] for c, p in caixas_com_peso])
            
            # linhas[k], colunas[k] = linha e coluna da k-ésima linha ordenada
            # pela menor coluna de cada um, em ordem crescente
            linhas = distancias.min(axis=1).argsort()
            colunas = distancias.argmin(axis=1)[linhas]

            colunas_usadas = set()

            for linha, coluna in zip(linhas, colunas):

                if coluna in colunas_usadas:
                    continue

                pessoa = self.pessoas[pessoas_ids[linha]]
                pessoa.atualizar(*caixas_com_peso[coluna][0], caixas_com_peso[coluna][1])
                colunas_usadas.add(coluna)

            if len(caixas_com_peso) > len(self.pessoas):
                self._registra_pessoas(
                    [c for (i, c) in enumerate(caixas_com_peso) if i not in colunas_usadas],
                    pos_original=pos_original
                )

        return self.pega_caixas_pessoas()



    def pega_caixas_pessoas(self, pos_final='cima-esquerda'):

        '''Retorna as caixas equivalentes às pessoas, com peso.

        Retorno é uma lista de tuplas [((x, y, w, h), peso), ...]

        Parametros:
            pos: posicão que a coordenada (x, y) representa. Pode ser:
                'centro',
                'cima',
                'baixo',
                'direita',
                'esquerda',
                'cima-esquerda' (padrão)
                'cima-direita',
                'baixo-esquerda',
                'baixo-direita'.
         '''

        pessoas_retorno = []
        for pessoa in self.pessoas.values():

            caixa, peso = pessoa.pega_caixa_com_peso()
            caixa = caixa_tools.muda_origem_caixa(*caixa, pos_original='centro', pos_final=pos_final)
            pessoas_retorno.append((caixa, peso))

        return pessoas_retorno

    def _atualiza_pessoas_desaparecidas(self):

        '''Atualiza o número de pessoas confirmadas e há quanto tempo cada pessoa está desaparecida.
        '''

        pessoas_confirmadas = 0
        for key, pessoa in list(self.pessoas.items()):
            pessoa.aumenta_tempo_desaparecida()
            if not pessoa.atingiu_limite_desaparecimento():
                del self.pessoas[key]
            elif pessoa.esta_confirmada():
                pessoas_confirmadas += 1
        
        self.pessoas_confirmadas = pessoas_confirmadas

        return self.pessoas_confirmadas
    

    def _registra_pessoas(self, caixas_com_peso, pos_original='cima-esquerda'):
        for caixa, peso in caixas_com_peso:
            self._registra_pessoa(*caixa, peso, pos_original=pos_original)

    def _registra_pessoa(self, x, y, w, h, peso, pos_original='cima-esquerda'):

        caixa = caixa_tools.muda_origem_caixa(x, y, w, h, pos_original=pos_original, pos_final='centro')
        self.pessoas[self.id_contador] = CaixaPessoa(
            x, y, w, h, peso, self.min_frames_para_confirmar, self.max_tempo_desaparecida
        )
        self.id_contador += 1


    def __len__(self):
        return len(self.pessoas)

    def __str__(self):

        return 'Pessoas: {}\n' 'Pessoas confirmadas: {}'.format(len(self), self.pessoas_confirmadas)
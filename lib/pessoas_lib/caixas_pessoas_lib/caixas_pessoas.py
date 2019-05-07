# -*- coding: utf-8 -*-

# Referências:
# https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
# https://stackoverflow.com/questions/29734660/python-numpy-keep-a-list-of-indices-of-a-sorted-2d-array

import numpy as np
from scipy.spatial import distance

from .caixa_pessoa import CaixaPessoa
from imagelib import caixa_tools

class CaixasPessoas:

    def __init__(self, min_frames_para_confirmar=2, max_tempo_desaparecida=5, precisao_minima=0.0):

        # self.pessoas, self.id_contador, self.pessoas_confirmadas
        self.reiniciar()
    
        # Levanta ValueError. Checa max_tempo_desaparecida e min_frames_para_confirmar.
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

        # Paça a origem para o centro.
        caixas_com_peso = [(caixa_tools.muda_origem_caixa(*c, pos_original=pos_original), p)
                           for c, p in caixas_com_peso if c[1] >= self.precisao_minima]

        if len(caixas_com_peso) == 0:
            pass
        elif len(self.pessoas) == 0:
            self.reiniciar()
            self._registra_pessoas(caixas_com_peso)

        else:
            pessoas_ids = list(self.pessoas.keys())
            pessoas_centroides = [p.pega_coordenadas() for p in self.pessoas.values()]

            # Cria matriz de distâncias pessoas x caixas.
            distancias = distance.cdist(pessoas_centroides, [c[:2] for c, p in caixas_com_peso])

            # Ordena as coordenadas da matriz de forma que os itens da matriz
            # distancias fiquem crescentes.
            # Para cada coordenada (p, c), p se refere à linha pessoa[p] e
            # c se refere à coluna caixa[c].
            dist_ordenadas_1d = distancias.argsort(axis=None, kind='mergesort')
            coordenadas_distancia_crescente = np.vstack(np.unravel_index(dist_ordenadas_1d, distancias.shape)).T

            pessoas_usadas = set()
            caixas_usadas = set()

            for p, c in coordenadas_distancia_crescente:

                if p in pessoas_usadas or c in caixas_usadas:
                    continue
                (x, y, w, h), peso = caixas_com_peso[c]
                pessoa = self.pessoas[pessoas_ids[p]]
                w_pessoa, h_pessoa = pessoa.pega_dimensoes()

                # Se a distância for maior que a diagonal da maior caixa, ignorar.
                if distancias[p, c] > 2*max((w**2+h**2)**0.5, (w_pessoa**2+h_pessoa**2)**0.5):
                    continue
                pessoa.atualizar(x, y, w, h, peso)
                
                pessoas_usadas.add(p)
                caixas_usadas.add(c)

            if len(caixas_usadas) < len(caixas_com_peso):
                caixas_nao_usadas = set(range(len(caixas_com_peso))).difference(caixas_usadas)
                self._registra_pessoas([cp for i, cp in enumerate(caixas_com_peso) if i in caixas_nao_usadas])

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
    

    def _registra_pessoas(self, caixas_com_peso):
        for caixa, peso in caixas_com_peso:
            self._registra_pessoa(*caixa, peso)

    def _registra_pessoa(self, x, y, w, h, peso):

        self.pessoas[self.id_contador] = CaixaPessoa(
            x, y, w, h, peso, self.min_frames_para_confirmar, self.max_tempo_desaparecida
        )
        self.id_contador += 1


    def __len__(self):
        return len(self.pessoas)

    def __str__(self):
        return 'Pessoas: {}\n' 'Pessoas confirmadas: {}'.format(len(self), self.pessoas_confirmadas)
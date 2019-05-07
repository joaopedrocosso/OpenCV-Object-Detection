# -*- coding: utf-8 -*-

import collections

class CaixaComPeso:
    
    def __init__(self, x, y, w, h, peso=None):

        '''Guarda as coordenadas de uma caixa em uma imagem e um percentual.

        Parâmetros:
            x, y: Coordenadas do centro da caixa. Números inteiro positivo.
            w, h: Largura e altura da caixa. Números inteiro positivo.
            peso: Percentual. Número real entre 0.0 e 1.0 incluso. Opcional.

        Métodos:
            atualizar: Modifica x, y, w, h e peso (opcional).
            pega_coordenadas: Retorna (x, y).
            pega_caixa: Retorna (x, y, w, h).
            pega_caixa_com_peso: Retorna ((x, y, w, h), peso).

        built_ins:
            __str__
        '''

        # Levantam ValueError
        self.x, self.y, self.w, self.h = self._checa_coordenadas_caixa(x, y, w, h)
        self.peso = self._checa_peso(peso)
        
    
    def atualizar(self, x, y, w, h, peso=None):
        
        # Levantam ValueError
        self.x, self.y, self.w, self.h = self._checa_coordenadas_caixa(x, y, w, h)
        self.peso = self._checa_peso(peso)


    def pega_coordenadas(self):
        return (self.x, self.y)
    def pega_dimensoes(self):
        return (self.w, self.h)
    def pega_caixa(self):
        return self.x, self.y, self.w, self.h
    def pega_caixa_com_peso(self):
        return self.pega_caixa(), self.peso


    def __str__(self):

        return '(x={}, y={}), (w={}, h={}), peso={}'.format(
            self.x, self.y, self.w, self.h, self.peso,
        )


    def _checa_peso(self, peso):

        if peso is not None:
            try:
                peso = float(peso)
                if peso < 0.0 or peso > 1.0:
                    raise ValueError
            except ValueError:
                raise ValueError('Peso deve ser um número real entre 0.0 e 1.0, inclusive.')

        return peso
    
    def _checa_coordenadas_caixa(self, x, y, w, h):
        
        '''Checa se as coordenadas da caixa fornecida é valida.

        Checa se as coordenadas (x, y) são números inteiros não-negativos
        e se 'w' e 'h' são inteiros positivos.

        Levanta ValueError.
        '''

        try:
            x = int(x)
            y = int(y)
            if x < 0 or y < 0:
                raise ValueError
        except ValueError:
            raise ValueError('Posicao (x, y) devem ser (ou poder ser convertidos para) inteiros positivos.')

        try:
            w = int(w)
            h = int(h)
            if w <= 0 or h <= 0:
                raise ValueError
        except ValueError:
            raise ValueError('Largura e altura devem ser (ou poder ser convertidos para) inteiros positivos.')

        return x, y, w, h
        
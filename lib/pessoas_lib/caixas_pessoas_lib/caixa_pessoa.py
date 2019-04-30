# -*- coding: utf-8 -*-

import collections

from imagelib.caixa_com_peso import CaixaComPeso

class CaixaPessoa(CaixaComPeso):
    
    def __init__(self, x, y, w, h, peso=None, min_frames_para_confirmar=1, max_tempo_desaparecida=5):

        '''Guarda informações relacionadas a uma pessoa detectada em uma imagem.

        Este objeto guarda uma caixa onde uma pessoa está localizada e a probabilidade dela ser, de fato, uma pessoa.
        Para evitar falsos positivos, a pessoa só é confirmada depois de aparecer por n frames.
        Depois de confirmada, ela só é desconfirmada (ou morta) após desaparecer por n frames.

        Parâmetros:
            x, y: Coordenadas do centro da caixa onde a pessoa está. Números inteiro positivo.
            w, h: Largura e altura da caixa. Números inteiro positivo.
            peso: Probabilidade de a pessoa ser, de fato, uma pessoa. Número real entre 0.0 e 1.0 incluso.
            min_frames_para_confirmar: Número mínimo de frames para remover noise. Número inteiro não-negativo.
            max_tempo_desaparecida: Número máximo de frames que a pessoa pode desaparecer antes de ser removida. Número inteiro não-negativo.

        Métodos:
            atualizar: Atualiza a caixa e o peso da pessoa, além de informar que a pessoa está presente.
            aumenta_tempo_desaparecida: Aumenta o tempo em que a pessoa desapareceu.
            is_viva: Checa se a pessoa não morreu.
            esta_confirmada: Checa se a pessoa foi confirmada como tal.
            pega_rastros: Retorna um iterador com os rastros da pessoa até um certo ponto.

            pega_coordenadas: Retorna as coordenadas (x, y).
            pega_caixa: Retorna caixa (x, y, w, h).
            pega_caixa_com_peso: Retorna caixa+peso ((x, y, w, h), peso).
    
        built-ins:
            __str__
            __len__

        '''

        # Levanta ValueError
        super().__init__(x, y, w, h, peso)

        try:
            self.min_frames_para_confirmar = int(min_frames_para_confirmar)
            if self.min_frames_para_confirmar < 0:
                raise ValueError
        except ValueError:
            raise ValueError("'min_frames_para_confirmar' deve ser um número inteiro não-negativo.")

        try:
            self.max_tempo_desaparecida = int(max_tempo_desaparecida)
            if self.max_tempo_desaparecida <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("'max_tempo_desaparecida' deve ser um número inteiro positivo.")

        self.rastros = collections.deque(maxlen=100)
        self.tempo_desaparecida = 0
        self.viva = True

        self.pessoa_confirmada = False
        self.frames_desde_criacao = 0
        
    
    def atualizar(self, x, y, w, h, peso=None):

        '''Atualiza as informações da pessoa.

        Atualiza a caixa com peso, o histórico de rastros e o contador de frames desde o início.
        Também informa que a pessoa não está desaparecida e a confirma, se já existir há um número
        suficiente de frames.
        '''

        if not self.viva:
            return
        
        x_antigo, y_antigo = self.x, self.y

        # Levanta ValueError
        super().atualizar(x, y, w, h, peso)
    
        self.rastros.append((x_antigo, y_antigo))
    
        self.frames_desde_criacao += 1 + self.tempo_desaparecida
        self.tempo_desaparecida = 0

        if not self.pessoa_confirmada and self.frames_desde_criacao >= self.min_frames_para_confirmar:
            self.pessoa_confirmada = True


    def aumenta_tempo_desaparecida(self):

        '''Aumenta tempo de desaparecimento e mata a pessoa, se continua desaparecida há muito tempo.'''

        if not self.viva:
            return

        self.tempo_desaparecida += 1
        if self.tempo_desaparecida > self.max_tempo_desaparecida:
            self.viva = False



    def atingiu_limite_desaparecimento(self):
        return self.viva
    def esta_confirmada(self):
        return self.pessoa_confirmada


    def pega_rastros(self):

        '''Retorna um iterador sobre os rastros da pessoa.'''
        return iter(self.rastros)


    def __str__(self):

        return '{}, {} e {}'.format(
            super().__str__(),
            'viva' if self.viva else 'morta',
            'confirmada' if self.pessoa_confirmada else 'nao confirmada'
        )
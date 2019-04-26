# -*- coding: utf-8 -*-

from .caixa_pessoa import CaixaPessoa

class CaixasPessoas:

    def __init__(self, min_frames_para_confirmar=1, max_tempo_desaparecida=10, precisao_minima=0.5):

        # self.pessoas, self.idContador, self.pessoasConfirmadas
        self.reiniciar()
    
        # Levanta ValueError. Checa max_tempo_desaparecida e precisao_minima.
        CaixaPessoa(100, 100, 1, 1, None, min_frames_para_confirmar, max_tempo_desaparecida)

        try:
            self.precisao_minima = float(precisao_minima)
            if not 0.0 <= self.precisao_minima <= 1.0:
                raise ValueError
        except ValueError:
            raise ValueError("'precisao_minima' deve ser um número real entre 0.0 e 1.0 inclusive.")


    def reiniciar(self):
        self.pessoas = {}
        self.idContador = 0
        self.pessoasConfirmadas = 0

    def atualizar(self, caixas_com_peso):

        '''Atualiza lista de pessoas.'''

        self._atualiza_pessoas_desaparecidas()

        if len(caixas_com_peso) == 0:
            return self.get_pessoas(pos='cima-esquerda')

        if len(self.pessoas) == 0:
            self.reiniciar()
            for (x, y, w, h), peso in caixas_com_peso:
                cx = x - w//2
                cy = y - h//2
                self._registra_pessoa(cx, cy, w, h, peso)
            return self.get_pessoas(pos='cima-esquerda')




    def get_caixas_pessoas(self, pos='centro'):

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

        pessoas_retorno = []
        for pessoa in self.pessoas:

            (x, y, w, h), peso = pessoa.get_caixas_com_peso()

            if pos in ['esquerda', 'cima-esquerda', 'baixo-esquerda']:
                x -= w//2
            elif pos in ['direita', 'cima-direita', 'baixo-direita']:
                x += w//2

            if pos_y in ['cima', 'cima-esquerda', 'cima-direita']:
                y -= h//2
            elif pos_y in ['baixo', 'baixo-esquerda', 'baixo-direita']:
                y += h//2

            pessoas_retorno.append( ((x, y, w, h), peso) )

        return pessoas_retorno

    def _atualiza_pessoas_desaparecidas(self):

        '''
        Atualiza o numero de pessoas confirmadas e ha quanto
        tempo cada pessoa esta desaparecida.
        '''

        for p in self.pessoas:
            p.aumenta_tempo_desaparecida()
            if not p.is_viva():
                indice = self.pessoas.index(p)
                self.pessoas.pop(indice)

        pessoas_novas = 0
        for p in self.pessoas:
            if p.is_confirmada():
                pessoas_novas+=1
        self.pessoas_confirmadas = pessoas_novas

        return self.pessoas_confirmadas
    
    def _registra_pessoa(self, x, y, w, h, peso):

        self.pessoas[self.id_contador] = CaixaPessoa(
            x, y, w, h, peso, self.min_frames_para_confirmar, self.max_tempo_desaparecida
        )
        self.id_contador += 1


    def __len__(self):
        return len(self.pessoas)

    def __str__(self):

        return 'Pessoas: {}\n' 'Pessoas confirmadas: {}'.format(len(self), self.pessoas_confirmadas)
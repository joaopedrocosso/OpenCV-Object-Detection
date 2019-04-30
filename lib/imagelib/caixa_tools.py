# -*- coding: utf-8 -*-

def muda_origem_caixa(x0, y0, w, h, pos_original='centro', pos_final='centro'):

    '''Retorna a caixa com a origem em outra posição.

    Parametros:
        pos_original: posição da origem original (x0, y0).
        pos_final: posição da origem modificada (xf, yf).
        Ambas podem ser:
            'centro', (padrao)
            'cima',
            'baixo',
            'direita',
            'esquerda',
            'cima-esquerda'
            'cima-direita',
            'baixo-esquerda',
            'baixo-direita'.
		x0, y0: origem original.
		xf, yf: origem final.
	
	Retorna (xf, yf, w, h).
    '''

    valor = {
        'cima-esquerda':(-1, -1),
        'cima':(0, -1),
        'cima-direita':(1, -1),
        'esquerda':(-1, 0),
        'centro':(0, 0),
        'direita':(1, 0),
        'baixo-esquerda':(-1, 1),
        'baixo':(0, 1),
        'baixo-direita':(1, 1)
    }

    x0_mod = valor[pos_original][0]
    y0_mod = valor[pos_original][1]
    xf_mod = valor[pos_final][0]
    yf_mod = valor[pos_final][1]

    xf = x0 + (xf_mod-x0_mod)*(w//2)
    yf = y0 + (yf_mod-y0_mod)*(h//2)

    return xf, yf, w, h
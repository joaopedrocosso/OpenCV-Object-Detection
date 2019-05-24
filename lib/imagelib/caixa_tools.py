# -*- coding: utf-8 -*-

def muda_origem_caixa(x0, y0, w, h, pos_original='centro', pos_final='centro'):

    '''Retorna a caixa com a origem em outra posição.

    Parameters
    -----------
    x0, y0 : int
        Origem original. (>= -w, -h)
    w, h : int
        Largura e altura. (> 0)
    pos_original, pos_final: : str
        Posição da origem original (x0, y0) e posição da origem
        modificada (xf, yf).
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
	
	Returns
    --------
    int, int, int, int
        Coordenadas da origem final x0 e y0, largura e altura.

    Raises
    ------
    ValueError
        Se ao menos um dos argumentos não estiver dentro dos limites
        especificados.
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
    
    if x0+w < 0 or y0+h < 0 or w <= 0 or h <= 0:
        raise ValueError("Coordenadas ou dimensões da caixa inválidas.")

    valores_chave = valor.keys()
    if pos_original not in valores_chave or pos_final not in valores_chave:
        raise ValueError("'pos_original' e 'pos_final' inválidos.")

    x0_mod = valor[pos_original][0]
    y0_mod = valor[pos_original][1]
    xf_mod = valor[pos_final][0]
    yf_mod = valor[pos_final][1]

    xf = x0 + (xf_mod-x0_mod)*(w//2)
    yf = y0 + (yf_mod-y0_mod)*(h//2)

    return xf, yf, w, h
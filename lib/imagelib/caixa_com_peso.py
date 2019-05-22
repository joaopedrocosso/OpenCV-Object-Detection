import collections

class CaixaComPeso:

    '''Guarda informações relacionadas a uma pessoa detectada em uma imagem.

    Este objeto guarda uma caixa onde uma pessoa está localizada e a 
    probabilidade dela ser, de fato, uma pessoa.

    Para evitar falsos positivos, a pessoa só é confirmada depois de 
    aparecer por n frames. Depois de confirmada, ela só é desconfirmada 
    (ou morta) após desaparecer por n frames.

    Parameters
    ----------
    x, y: int
        Coordenadas do centro da caixa onde a pessoa está.
        ('x', 'y' >= 0)
    w, h : int
        Largura e altura da caixa. ('w', 'h' > 0)
    peso : float, optional
        Probabilidade, se houver, de a pessoa ser, de fato, uma pessoa.
        Deve estar em [0.0, 1.0] ou ser 'None'. (Padrão=None)

    Raises
    -------
    ValueError
        Se um dos valores não estiver dentro do especificado.
    '''
    
    def __init__(self, x, y, w, h, peso=None):
        # Levantam ValueError
        self.x, self.y, self.w, self.h = self._checa_coordenadas_caixa(x, y, w, h)
        self.peso = self._checa_peso(peso)
        
    
    def atualizar(self, x, y, w, h, peso=None):
        '''Atualiza as informações da pessoa.

        Parameters
        -----------
        x, y : int
            Coordenadas novas da caixa. (>= 0)
        w, h : int
            Largura e altura novas da caixa. (> 0)
        peso : float, optional
            Novo peso da caixa, se houver.
            (No período [0.0, 1.0], ou None) (Padrão=None)

        Raises
        -------
        ValueError
            Se um dos parâmetros não estiver dentro do especificado.
        '''

        # Levantam ValueError
        self.x, self.y, self.w, self.h = self._checa_coordenadas_caixa(x, y, w, h)
        self.peso = self._checa_peso(peso)


    def pega_coordenadas(self):
        '''Pega as coordenadas da caixa.
        Returns
        -----------
        tuple of int
            Coordenadas x e y.
        '''
        return (self.x, self.y)

    def pega_dimensoes(self):
        '''Pega as dimensões da caixa.
        Returns
        --------
        tuple of int
            Largura e altura.
        '''
        return (self.w, self.h)

    def pega_caixa(self):
        '''Pega coordenadas e dimensões da caixa.
        Returns
        --------
        tuple of int
            Coordenadas x e y, largura e altura.
        '''
        return self.x, self.y, self.w, self.h
    def pega_caixa_com_peso(self):
        '''Pega coordenadas, dimensões da caixa e um peso.
        Returns
        --------
        ((int, int, int, int), float)
            Coordenadas x e y, largura, altura, em uma tupla, mais um
            peso.
        '''
        return self.pega_caixa(), self.peso


    def __str__(self):
        '''Representação em string do objeto.
        
        Returns
        -------
        str
        '''
        return '(x={}, y={}), (w={}, h={}), peso={}'.format(
            self.x, self.y, self.w, self.h, self.peso,
        )


    def _checa_peso(self, peso):
        '''Levanta exceção se o peso for inválido.

        Parameters
        ----------
        peso : float
            Peso desejado.

        Returns
        --------
        float
            O próprio peso.

        Raises
        -------
        ValueError
            Se o peso não for None e nem estiver entre 0.0 e 1.0, incl. 
        '''

        if peso is not None:
            try:
                peso = float(peso)
                if peso < 0.0 or peso > 1.0:
                    raise ValueError
            except ValueError:
                raise ValueError(
                    'Peso deve ser um número real entre 0.0 e 1.0, inclusive.')

        return peso
    
    def _checa_coordenadas_caixa(self, x, y, w, h):
        
        '''Levanta exceção se o peso for inválido.

        Parameters
        ----------
        x, y, w, h : int
            Coordenadas, largura e altura da caixa.

        Returns
        --------
        (int, int, int, int)
            Os próprios argumentos do método.

        Raises
        -------
        ValueError
            Se x, y < 0 ou w, h <= 0.
        '''

        try:
            x = int(x)
            y = int(y)
            if x < 0 or y < 0:
                raise ValueError
        except ValueError:
            raise ValueError(
                'Posicao (x, y) devem ser (ou poder ser convertidos para) '
                'inteiros positivos.')

        try:
            w = int(w)
            h = int(h)
            if w <= 0 or h <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(
                'Largura e altura devem ser (ou poder ser convertidos para) '
                'inteiros positivos.')

        return x, y, w, h
        
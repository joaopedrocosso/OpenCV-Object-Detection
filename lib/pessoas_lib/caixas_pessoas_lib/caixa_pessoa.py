import collections

from imagelib.caixa_com_peso import CaixaComPeso

class CaixaPessoa(CaixaComPeso):

    '''Guarda informações relacionadas a uma pessoa detectada em uma imagem.

    Este objeto guarda uma caixa onde uma pessoa está localizada e a 
    probabilidade dela ser, de fato, uma pessoa.

    Para evitar falsos positivos, a pessoa só é confirmada depois de 
    aparecer por n frames. Depois de confirmada, ela só é desconfirmada 
    (ou morta) após desaparecer por n frames.

    Parameters
    -----------
    x, y: int
        Coordenadas do centro da caixa onde a pessoa está.
        ('x', 'y' >= -'w', -'h')
    w, h : int
        Largura e altura da caixa. ('w', 'h' > 0)
    peso : float, optional
        Probabilidade, se houver, de a pessoa ser, de fato, uma pessoa.
        Deve estar em [0.0, 1.0] ou ser 'None'. (Padrão=None)
    min_frames_para_confirmar : int, optional
        Número mínimo de frames para a pessoa registrada ser confirmada
        como pessoa. Serve para remover falsos positivos. (>= 1)
        (Padrão=1)
    max_tempo_desaparecida : int, optional
        Número máximo de frames que a pessoa pode desaparecer antes de 
        ser removida. (>0) e (Padrão=5)

    Raises
    -------
    ValueError
        Se um dos valores não estiver dentro do especificado.
    '''
    
    def __init__(self, x, y, w, h, peso=None, min_frames_para_confirmar=1,
                 max_tempo_desaparecida=5):

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

        Parameters
        -----------
        x, y : int
            Coordenadas novas da caixa. (>= -'w', -'h')
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

        '''
        Aumenta tempo de desaparecimento e mata a pessoa, se continua 
        desaparecida há muito tempo.
        '''
        if not self.viva:
            return

        self.tempo_desaparecida += 1
        if self.tempo_desaparecida > self.max_tempo_desaparecida:
            self.viva = False


    def atingiu_limite_desaparecimento(self):
        '''Retorna se a pessoa já desapareceu há muito tempo, ou não.

        Returns
        -------
        bool
        '''
        return not self.viva

    def esta_confirmada(self):
        '''Retorna se a caixa já foi confirmada como pessoa.

        Returns
        -------
        bool
        '''
        return self.pessoa_confirmada

    def esta_desaparecida(self):
        '''Retorna se a pessoa está desaparecida.

        Returns
        --------
        bool
        '''
        return self.tempo_desaparecida > 0


    def pega_rastros(self):
        '''Retorna um iterador sobre os rastros da pessoa.

        Returns
        --------
        iterator
        '''
        return iter(self.rastros)


    def __str__(self):
        '''Representação em string do objeto.
        
        Returns
        -------
        str
        '''

        return '{}, {} e {}'.format(
            super().__str__(),
            'viva' if self.viva else 'morta',
            'confirmada' if self.pessoa_confirmada else 'nao confirmada'
        )
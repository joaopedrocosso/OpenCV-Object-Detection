import collections

from imagelib.caixa_com_peso import CaixaComPeso

class CaixaObjeto(CaixaComPeso):

    '''Guarda informações relacionadas a um objeto detectado em uma imagem.

    Esta classe guarda uma caixa onde um objeto está localizado e a 
    probabilidade dele ser o tipo de objeto que se espera.

    Para evitar falsos positivos, o objeto só é confirmado depois de 
    aparecer por n frames. Depois de confirmado, ele só é desconfirmado 
    (ou morto) após desaparecer por n frames.

    Parameters
    -----------
    x, y: int
        Coordenadas do centro da caixa onde o objeo está.
        ('x', 'y' >= -'w', -'h')
    w, h : int
        Largura e altura da caixa. ('w', 'h' > 0)
    peso : float, optional
        Probabilidade do objeto ser do tipo esperado.
        Deve estar em [0.0, 1.0] ou ser 'None'. (Padrão=None)
    min_frames_para_confirmar : int, optional
        Número mínimo de frames para o objeto registrado ser confirmado.
        Serve para remover falsos positivos. (>= 0)
        (Padrão=0)
    max_tempo_desaparecido : int, optional
        Número máximo de frames em que o objeto pode desaparecer antes de 
        ser removido. (>= 0) e (Padrão=5)

    Raises
    -------
    ValueError
        Se um dos valores não estiver dentro do especificado.
    '''
    
    def __init__(self, x, y, w, h, peso=None, min_frames_para_confirmar=0,
                 max_tempo_desaparecido=0):

        # Levanta ValueError
        super().__init__(x, y, w, h, peso)
        try:
            self.min_frames_para_confirmar = int(min_frames_para_confirmar)
            if self.min_frames_para_confirmar < 0:
                raise ValueError
        except ValueError:
            raise ValueError(
                "'min_frames_para_confirmar' deve ser um número inteiro "
                "não-negativo.")

        try:
            self.max_tempo_desaparecido = int(max_tempo_desaparecido)
            if self.max_tempo_desaparecido < 0:
                raise ValueError
        except ValueError:
            raise ValueError(
                "'max_tempo_desaparecido' deve ser um número não "
                "negativo.")

        self.rastros = collections.deque(maxlen=100)
        self.tempo_desaparecido = 0
        self.vivo = True

        self.objeto_confirmado = (self.min_frames_para_confirmar == 0)
        self.frames_desde_criacao = 0
        
    
    def atualizar(self, x, y, w, h, peso=None):

        '''Atualiza as informações do objeto.

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

        if not self.vivo:
            return
        
        x_antigo, y_antigo = self.x, self.y

        # Levanta ValueError
        super().atualizar(x, y, w, h, peso)
    
        self.rastros.append((x_antigo, y_antigo))
    
        self.frames_desde_criacao += 1 + self.tempo_desaparecido
        self.tempo_desaparecido = 0

        if not self.objeto_confirmado and self.frames_desde_criacao >= self.min_frames_para_confirmar:
            self.objeto_confirmado = True


    def aumenta_tempo_desaparecido(self):

        '''
        Aumenta tempo de desaparecimento e mata o objeto, se continuar 
        desaparecido por muito tempo.
        '''
        if not self.vivo:
            return

        self.tempo_desaparecido += 1
        if self.tempo_desaparecido >= self.max_tempo_desaparecido:
            self.vivo = False


    def atingiu_limite_desaparecimento(self):
        '''Retorna se o objeto já desapareceu há muito tempo, ou não.

        Returns
        -------
        bool
        '''
        return not self.vivo

    def esta_confirmado(self):
        '''Retorna se a caixa já foi confirmada como um objeto.

        Returns
        -------
        bool
        '''
        return self.objeto_confirmado

    def esta_desaparecido(self):
        '''Retorna se o objeto está desaparecido.

        Returns
        --------
        bool
        '''
        return self.tempo_desaparecido > 0


    def pega_rastros(self):
        '''Retorna um iterador sobre os rastros do objeto.

        Returns
        --------
        iterator
        '''
        return iter(self.rastros)


    def __str__(self):
        '''Representação em string da instância.
        
        Returns
        -------
        str
        '''

        return '{}, {} e {}'.format(
            super().__str__(),
            'vivo' if self.vivo else 'morto',
            'confirmado' if self.objeto_confirmado else 'não confirmado'
        )
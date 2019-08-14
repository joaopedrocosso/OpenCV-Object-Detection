# Referências:
# https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
# https://stackoverflow.com/questions/29734660/python-numpy-keep-a-list-of-indices-of-a-sorted-2d-array

import numpy as np
from scipy.spatial import distance

from .caixa_objeto import CaixaObjeto
from imagelib import caixa_tools

class CaixasObjetos:

    '''Registra caixas que representam objetos em um vídeo.

    Parameters
    -----------
    min_frames_para_confirmar : int, optional
        Número mínimo de frames para uma caixa ser confirmada como um
        objeto e não um falso positivo. (>= 0) (Padrão=2)
    max_tempo_desaparecido : int, optional
        Tempo máximo que uma caixa pode sumir do vídeo antes de ser
        descartada do registro. (>= 0) (Padrão=0)
    precisao_minima : float, optional
        Probabilidade mínima da caixa ser um objeto para que seja
        aceita no registro. (em [0.0, 1.0]) (Padrão=0.0)
    
    Raises
    -------
    ValueError
        Se os parâmetros não seguirem as especificações.
    '''

    def __init__(self, min_frames_para_confirmar=0, max_tempo_desaparecido=0,
                 precisao_minima=0.0):
        # self.objetos, self.id_contador, self.objetos_confirmados
        self.reiniciar()
    
        # Levanta ValueError. Checa max_tempo_desaparecido e
        # min_frames_para_confirmar.
        CaixaObjeto(100, 100, 1, 1, None, min_frames_para_confirmar,
                    max_tempo_desaparecido)
        self.min_frames_para_confirmar = int(min_frames_para_confirmar)
        self.max_tempo_desaparecido = int(max_tempo_desaparecido)

        try:
            self.precisao_minima = float(precisao_minima)
            if not 0.0 <= self.precisao_minima <= 1.0:
                raise ValueError
        except ValueError:
            raise ValueError(
                "'precisao_minima' deve ser um número real entre 0.0 e 1.0 "
                "inclusive.")


    def reiniciar(self):
        '''Reinicia as caixas para zero.'''
        self.objetos = {}
        self.id_contador = 0
        self.objetos_confirmados = 0

        # Cópia de self.objetos, a fim de evitar conflitos de concorrência.
        # Guarda as coordenadas e pesos dos objetos em tuplas da forma:
        # [((int, int, int, int), float), ...]
        self.objetos_externo = []


    def atualizar(self, caixas=None, pesos=None, pos_original='cima-esquerda',
                  caixas_paradas=False):
        '''Atualiza o registro de objetos.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...], optional
            Caixas (x, y, w, h). x >= -w, y >= -h, w,h > 0.
            Desnecessário se 'caixas_paradas'=True
        pesos : [float, ...], optional
            Probabilidades de cada caixa representar um objeto. Deve
            estar entre 0.0 e 1.0, inclusive.
            Desnecessário se 'caixas_paradas'=True
        pos_original : str, optional
            Posição na qual a origem da caixa se encontra. Opções
            incluem:
            'centro',
            'cima',
            'baixo',
            'direita',
            'esquerda',
            'cima-esquerda' (padrão)
            'cima-direita',
            'baixo-esquerda',
            'baixo-direita'.
            Desnecessário se 'caixas_paradas'=True
        caixas_paradas : bool
            Quando as caixas desta chamada são as mesmas da anterior.
            Neste caso, os dados da chamada anterior são usados sem
            olhar as caixas ou pesos..

        Returns
        --------
        caixas : [(int, int, int, int), ...]
            Todas as caixas registradas e confirmadas como objetos.
        pesos : [float, ...]
            Probabilidade das caixas representarem objetos.

        Raises
        -------
        ValueError
            Se as caixas ou pesos não forem fornecidos e 
            'caixas_paradas' for falso ou algum dos parâmetros não 
            bater as especificações.
        '''
        if caixas_paradas:
            self._atualizar_repetir_iteracao()
        else:
            if caixas is None or pesos is None:
                raise ValueError(
                    "'caixas' e 'pesos' devem ser preenchidos se 'caixas_paradas'"
                    " for False."
                )
            # Levanta ValueError
            self._atualizar_caixas_novas(caixas, pesos, pos_original)
        
        self._copia_objetos_uso_externo()

        return self.pega_objetos()


    def _atualizar_caixas_novas(self, caixas, pesos, pos_original):
        '''
        Atualiza o registro de objetos, comparando os objetos 
        registrados com as caixas novas.

        Deve ser chamado pelo método 'atualizar'.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...]
            Caixas (x, y, w, h). x >= -w, y >= -h, w,h > 0.
        pesos : [float, ...]
            Probabilidades de cada caixa representar um objeto. Devem
            estar entre 0.0 e 1.0, inclusive, ou serem None.
        pos_original : str, optional
            Posição na qual a origem da caixa se encontra. Opções
            incluem:
            'centro',
            'cima',
            'baixo',
            'direita',
            'esquerda',
            'cima-esquerda' (padrão)
            'cima-direita',
            'baixo-esquerda',
            'baixo-direita'.

        Raises
        -------
        ValueError
            Se algum dos parâmetros não bater as especificações.
        '''
        # Passa a origem para o centro.
        caixas = [caixa_tools.muda_origem_caixa(*c, pos_original=pos_original)
                  for c in caixas]
        # len(pesos) será >= len(caixas).
        pesos.extend([None]*(len(caixas)-len(pesos)))
        caixas, pesos = self._remove_pesos_pequenos(caixas, pesos)

        if len(caixas) == 0:
            self._aumentar_desaparecimento()
        elif len(self.objetos) == 0:
            self.reiniciar()
            # Levanta ValueError.
            self._registra_objetos(caixas, pesos)

        else:
            objetos_ids = list(self.objetos.keys())
            objetos_centroides = [
                o[:2] for o in self.pega_objetos(pos_final='centro', retorna_peso=False)]

            # Cria matriz de distâncias objetos x caixas.
            distancias = distance.cdist(
                objetos_centroides, [c[:2] for c in caixas])

            # Ordena as coordenadas da matriz de forma que os itens da matriz
            # distancias fiquem crescentes.
            # Para cada coordenada (o, c), o se refere à linha objeto[o] e
            # c se refere à coluna caixa[c].
            dist_ordenadas_1d = distancias.argsort(axis=None, kind='mergesort')
            coordenadas_distancia_crescente = np.vstack(
                    np.unravel_index(dist_ordenadas_1d, distancias.shape)).T

            objetos_usados = set()
            caixas_usadas = set()

            for o, c in coordenadas_distancia_crescente:

                if o in objetos_usados or c in caixas_usadas:
                    continue
                (x, y, w, h), peso = caixas[c], pesos[c]
                objeto = self.objetos[objetos_ids[o]]
                w_objeto, h_objeto = objeto.pega_dimensoes()

                # Se a distância for maior que a diagonal da maior caixa, ignorar.
                if distancias[o, c] > 2*max((w**2+h**2)**0.5,
                                            (w_objeto**2+h_objeto**2)**0.5):
                    continue
                objeto.atualizar(x, y, w, h, peso)
                
                objetos_usados.add(o)
                caixas_usadas.add(c)

                if (len(objetos_usados) == len(objetos_ids)
                    or len(caixas_usadas) == len(caixas)):
                    #
                    break

            if len(caixas_usadas) < len(caixas):
                caixas_nao_usadas = (set(range(len(caixas)))
                                    .difference(caixas_usadas)) 
                # Levanta ValueError.
                self._registra_objetos(
                    [c for i, c in enumerate(caixas)
                     if i in caixas_nao_usadas],
                    [peso for i, peso in enumerate(pesos)
                     if i in caixas_nao_usadas])
            
            if len(objetos_usados) < len(objetos_ids):
                objetos_nao_usados = (set(range(len(objetos_ids)))
                                      .difference(objetos_usados))
                self._aumentar_desaparecimento(
                    [objetos_ids[o] for o in objetos_nao_usados])


    def _atualizar_repetir_iteracao(self):
        '''Repete o que foi feito na iteração anterior'''
        objetos_atualizadas = set()
        for chave, objeto in list(self.objetos.items()):
            if not objeto.esta_desaparecido():
                objeto.atualizar(*objeto.pega_caixa(), objeto.pega_peso())
                objetos_atualizadas.add(chave)

        objetos_desaparecidas = (set(list(self.objetos.keys()))
                                 .difference(objetos_atualizadas))
        self._aumentar_desaparecimento(objetos_desaparecidas)
        

    def _aumentar_desaparecimento(self, ids=None):
        '''Aumenta o desaparecimento de objetos.

        Parameters
        -----------
        ids : iterable of int, optional
            Chaves das objetos que terão seus desaparecimentos
            aumentados. Se não fornecido, todos os objetos terão
            seu desaparecimento aumentado.
        '''

        if ids is None:
            ids = list(self.objetos.keys())
        for chave in ids:
            objeto = self.objetos[chave]
            objeto.aumenta_tempo_desaparecido()
            if objeto.atingiu_limite_desaparecimento():
                self._retira_objeto(chave)
                

    def pega_objetos(self, pos_final='cima-esquerda', retorna_peso=True):

        '''Retorna as caixas equivalentes às objetos.

        Parameters
        -----------
        pos : str, optional
            Posicão que a coordenada (x, y) representa. Pode ser:
            'centro',
            'cima',
            'baixo',
            'direita',
            'esquerda',
            'cima-esquerda' (padrão)
            'cima-direita',
            'baixo-esquerda',
            'baixo-direita'.
        retorna_peso : bool, optional
            Se verdadeiro, retorna a probabilidade das caixas
            representarem objetos junto às caixas. (Padrão=True)

        Returns
        --------
        caixas : [(int, int, int, int), ...]
            Caixas equivalentes, no formato (xf, yf, w, h).
        pesos : [float, ...], optional
            Probabilidade das caixas representarem objetos. Só é
            retornado se 'retorna_peso' for verdadeiro.

        Raises
        -------
        ValueError
            Se ao menos uma das caixas tiver [x, y < -w, -h] ou w, h <= 0 ou
            o 'pos_final' não estiver dentro dos valores especificados.
         '''

        objetos_externo = self.objetos_externo
        objetos_retorno = []
        pesos_retorno = []
        for objeto in objetos_externo:
            caixa = objeto[0]
            caixa = caixa_tools.muda_origem_caixa(
                *caixa, pos_original='centro', pos_final=pos_final)
            objetos_retorno.append(caixa)
            if retorna_peso:
                pesos_retorno.append(objeto[1])

        if retorna_peso:
            return objetos_retorno, pesos_retorno
        else:
            return objetos_retorno


    def _copia_objetos_uso_externo(self):
        '''
        Copia as coordenadas dos objetos para uma lista, com o fim de
        não causar problemas de concorrência.
        '''
        objetos_externo = []
        for objeto in self.objetos.values():
            if not objeto.esta_confirmado():
                continue
            objetos_externo.append(objeto.pega_caixa_com_peso())
        
        self.objetos_externo = objetos_externo

    def _registra_objetos(self, caixas, peso):
        '''Registra novas caixas que representam objetos.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...]
            Caixas (x, y, w, h). x >= -w, y >= -h, w,h > 0.
        pesos : [float, ...]
            Probabilidades de cada caixa representar um objeto. Devem
            estar entre 0.0 e 1.0, inclusive, ou serem None.

        Raises
        -------
        ValueError
            Se os valores de caixas ou de peso forem inválidos.
        '''
        for caixa, peso in zip(caixas, peso):
            self._registra_objeto(*caixa, peso)

    def _registra_objeto(self, x, y, w, h, peso=None):
        '''Registra nova caixa que representa uma objeto.

        Parameters
        -----------
        x, y : int
            Coordenadas x e y do centro da caixa. Devem ser >= (-w, -h).
        w, h : int
            Largura e altura da caixa. Devem ser maiores que 0.
        peso : float
            Probabilidade da caixa representar, de fato, um objeto.
            Devem estar entre 0.0 e 1.0 incluso.

        Raises
        -------
        ValueError
            Se os argumentos não seguirem as restrições.
        '''
        self.objetos[self.id_contador] = CaixaObjeto(
            x, y, w, h, peso, self.min_frames_para_confirmar, self.max_tempo_desaparecido
        )
        self.id_contador += 1

    def _retira_objeto(self, id):
        '''Retira um objeto do registro de objetos.

        Parameters
        -----------
        id : int
            ID do objeto.

        Raises
        -------
        KeyError
            Se o ID for inválido.
        '''
        try:
            del self.objetos[id]
        except KeyError:
            raise KeyError('ID inválido.')
    
    def _remove_pesos_pequenos(self, caixas, pesos):
        '''
        Retorna somente as caixas e pesos que tem probabilidade maior
        ou igual que 'self.precisao_minima' ou que são None.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...]
            Caixas que representam objetos.
        pesos : [float, ...]
            Probabilidades de cada caixa representar um objeto. Podem
            ser None.
        
        Returns
        --------
        caixas : [(int, int, int, int)]
            Somente as caixas cujos pesos forem maiores ou iguais que 
            'self.precisao_minima'.
        pesos : [float, ...]
            Somente os pesos maiores ou iguais a 'self.precisao_minima'
            ou None.

        Raises
        -------
        ValueError
            Se ao menos um dos pesos for menor que 0.0 ou maior que 1.0.
        '''
        novo_caixas, novo_pesos = [], []
        for c, p in zip(caixas, pesos):
            if p is not None and (p < 0.0 or p > 1.0):
                raise ValueError(
                    'Pesos devem estar entre 0.0 e 1.0, incl., ou serem None.')
            if p is None or p >= self.precisao_minima:
                novo_caixas.append(c)
                novo_pesos.append(p)
        return novo_caixas, novo_pesos


    def __len__(self):
        '''Retorna o número de objetos registrados.

        Returns
        --------
        int
        '''
        return len(self.objetos)

    def __str__(self):
        '''Representação em string do objeto.
        
        Returns
        -------
        str
        '''
        return ('Objetos: {}\n' 'Objetos confirmadas: {}'
                .format(len(self), self.objetos_confirmados))
# Referências:
# https://www.pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/
# https://stackoverflow.com/questions/29734660/python-numpy-keep-a-list-of-indices-of-a-sorted-2d-array

import numpy as np
from scipy.spatial import distance

from .caixa_pessoa import CaixaPessoa
from imagelib import caixa_tools

class CaixasPessoas:

    '''Registra caixas que representam pessoas em um vídeo.

    Parameters
    -----------
    min_frames_para_confirmar : int, optional
        Número mínimo de frames para uma caixa ser aceita como pessoa. 
        (>= 0) (Padrão=2)
    max_tempo_desaparecida : int, optional
        Tempo máximo que uma caixa pode sumir do vídeo antes de ser
        descartada do registro. (>= 0) (Padrão=0)
    precisao_minima : float, optional
        Probabilidade mínima da caixa ser uma pessoa para que seja
        aceita no registro. (em [0.0, 1.0]) (Padrão=0.0)
    
    Raises
    -------
    ValueError
        Se os parâmetros não seguirem as especificações.
    '''

    def __init__(self, min_frames_para_confirmar=0, max_tempo_desaparecida=0,
                 precisao_minima=0.0):
        # self.pessoas, self.id_contador, self.pessoas_confirmadas
        self.reiniciar()
    
        # Levanta ValueError. Checa max_tempo_desaparecida e
        # min_frames_para_confirmar.
        CaixaPessoa(100, 100, 1, 1, None, min_frames_para_confirmar,
                    max_tempo_desaparecida)
        self.min_frames_para_confirmar = int(min_frames_para_confirmar)
        self.max_tempo_desaparecida = int(max_tempo_desaparecida)

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
        self.pessoas = {}
        self.id_contador = 0
        self.pessoas_confirmadas = 0


    def atualizar(self, caixas=None, pesos=None, pos_original='cima-esquerda',
                  caixas_paradas=False):
        '''Atualiza lista de pessoas.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...], optional
            Caixas (x, y, w, h). x >= -w, y >= -h, w,h > 0.
            Desnecessário se 'caixas_paradas'=True
        pesos : [float, ...], optional
            Probabilidades de cada caixa representar uma pessoa. Deve
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
            Todas as caixas registradas como pessoas.
        pesos : [float, ...]
            Probabilidade das caixas representarem pessoas.

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
        return self.pega_pessoas()


    def _atualizar_caixas_novas(self, caixas, pesos, pos_original):
        '''
        Atualiza a lista de pessoas, comparando as pessoas registradas
        com as caixas novas.

        Deve ser chamado pelo método 'atualizar'.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...]
            Caixas (x, y, w, h). x >= -w, y >= -h, w,h > 0.
        pesos : [float, ...]
            Probabilidades de cada caixa representar uma pessoa. Devem
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
        elif len(self.pessoas) == 0:
            self.reiniciar()
            # Levanta ValueError.
            self._registra_pessoas(caixas, pesos)

        else:
            pessoas_ids = list(self.pessoas.keys())
            pessoas_centroides = [
                p.pega_coordenadas() for p in self.pessoas.values()]

            # Cria matriz de distâncias pessoas x caixas.
            distancias = distance.cdist(
                pessoas_centroides, [c[:2] for c in caixas])

            # Ordena as coordenadas da matriz de forma que os itens da matriz
            # distancias fiquem crescentes.
            # Para cada coordenada (p, c), p se refere à linha pessoa[p] e
            # c se refere à coluna caixa[c].
            dist_ordenadas_1d = distancias.argsort(axis=None, kind='mergesort')
            coordenadas_distancia_crescente = np.vstack(
                    np.unravel_index(dist_ordenadas_1d, distancias.shape)).T

            pessoas_usadas = set()
            caixas_usadas = set()

            for p, c in coordenadas_distancia_crescente:

                if p in pessoas_usadas or c in caixas_usadas:
                    continue
                (x, y, w, h), peso = caixas[c], pesos[c]
                pessoa = self.pessoas[pessoas_ids[p]]
                w_pessoa, h_pessoa = pessoa.pega_dimensoes()

                # Se a distância for maior que a diagonal da maior caixa, ignorar.
                if distancias[p, c] > 2*max((w**2+h**2)**0.5,
                                            (w_pessoa**2+h_pessoa**2)**0.5):
                    continue
                pessoa.atualizar(x, y, w, h, peso)
                
                pessoas_usadas.add(p)
                caixas_usadas.add(c)

                if (len(pessoas_usadas) == len(pessoas_ids)
                    or len(caixas_usadas) == len(caixas)):
                    #
                    break

            if len(caixas_usadas) < len(caixas):
                caixas_nao_usadas = (set(range(len(caixas)))
                                    .difference(caixas_usadas)) 
                # Levanta ValueError.
                self._registra_pessoas(
                    [c for i, c in enumerate(caixas)
                     if i in caixas_nao_usadas],
                    [peso for i, peso in enumerate(pesos)
                     if i in caixas_nao_usadas])
            
            if len(pessoas_usadas) < len(pessoas_ids):
                pessoas_nao_usadas = (set(range(len(pessoas_ids)))
                                      .difference(pessoas_usadas))
                self._aumentar_desaparecimento(
                    [pessoas_ids[p] for p in pessoas_nao_usadas])


    def _atualizar_repetir_iteracao(self):
        '''Repete o que foi feito na iteração anterior'''
        pessoas_atualizadas = set()
        for chave, pessoa in list(self.pessoas.items()):
            if not pessoa.esta_desaparecida():
                pessoa.atualizar(*pessoa.pega_caixa(), pessoa.pega_peso())
                pessoas_atualizadas.add(chave)

        pessoas_desaparecidas = (set(list(self.pessoas.keys()))
                                 .difference(pessoas_atualizadas))
        self._aumentar_desaparecimento(pessoas_desaparecidas)
        

    def _aumentar_desaparecimento(self, ids=None):
        '''Aumenta o desaparecimento de pessoas.

        Parameters
        -----------
        ids : iterable of int, optional
            Chaves das pessoas que terão seus desaparecimentos
            aumentados. Se não fornecido, todas as pessoas terão
            seu desaparecimento aumentado.
        '''

        if ids is None:
            ids = list(self.pessoas.keys())
        for chave in ids:
            pessoa = self.pessoas[chave]
            pessoa.aumenta_tempo_desaparecida()
            if pessoa.atingiu_limite_desaparecimento():
                self._retira_pessoa(chave)
                

    def pega_pessoas(self, pos_final='cima-esquerda', retorna_peso=True):

        '''Retorna as caixas equivalentes às pessoas.

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
            representarem pessoas junto às caixas. (Padrão=True)

        Returns
        --------
        caixas : [(int, int, int, int), ...]
            Caixas equivalentes, no formato (xf, yf, w, h).
        pesos : [float, ...], optional
            Probabilidade das caixas representarem pessoas. Só é
            retornado se 'retorna_peso' for verdadeiro.

        Raises
        -------
        ValueError
            Se ao menos uma das caixas tiver [x, y < -w, -h] ou w, h <= 0 ou
            o 'pos_final' não estiver dentro dos valores especificados.
         '''

        pessoas_retorno = []
        pesos_retorno = []
        for pessoa in self.pessoas.values():
            if not pessoa.esta_confirmada():
                continue
            caixa = pessoa.pega_caixa()
            caixa = caixa_tools.muda_origem_caixa(
                *caixa, pos_original='centro', pos_final=pos_final)
            pessoas_retorno.append(caixa)
            if retorna_peso:
                pesos_retorno.append(pessoa.pega_peso())

        if retorna_peso:
            return pessoas_retorno, pesos_retorno
        else:
            return pessoas_retorno


    def _registra_pessoas(self, caixas, peso):
        '''Registra novas caixas que representam pessoas.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...]
            Caixas (x, y, w, h). x >= -w, y >= -h, w,h > 0.
        pesos : [float, ...]
            Probabilidades de cada caixa representar uma pessoa. Devem
            estar entre 0.0 e 1.0, inclusive, ou serem None.

        Raises
        -------
        ValueError
            Se os valores de caixas ou de peso forem inválidos.
        '''
        for caixa, peso in zip(caixas, peso):
            self._registra_pessoa(*caixa, peso)

    def _registra_pessoa(self, x, y, w, h, peso=None):
        '''Registra nova caixa que representa uma pessoa.

        Parameters
        -----------
        x, y : int
            Coordenadas x e y do centro da caixa. Devem ser >= (-w, -h).
        w, h : int
            Largura e altura da caixa. Devem ser maiores que 0.
        peso : float
            Probabilidade da caixa representar, de fato, uma pessoa.
            Devem estar entre 0.0 e 1.0 incluso.

        Raises
        -------
        ValueError
            Se os argumentos não seguirem as restrições.
        '''
        self.pessoas[self.id_contador] = CaixaPessoa(
            x, y, w, h, peso, self.min_frames_para_confirmar, self.max_tempo_desaparecida
        )
        self.id_contador += 1

    def _retira_pessoa(self, id):
        '''Retira uma pessoa do registro de pessoas.

        Parameters
        -----------
        id : int
            ID da pessoa.

        Raises
        -------
        KeyError
            Se o ID for inválido.
        '''
        try:
            del self.pessoas[id]
        except KeyError:
            raise KeyError('ID inválido.')
    
    def _remove_pesos_pequenos(self, caixas, pesos):
        '''
        Retorna somente as caixas e pesos que tem probabilidade maior
        ou igual que 'self.precisao_minima' ou que são None.

        Parameters
        -----------
        caixas : [(int, int, int, int), ...]
            Caixas que representam pessoas.
        pesos : [float, ...]
            Probabilidades de cada caixa representar uma pessoa. Podem
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
        '''Retorna o número de pessoas registradas.

        Returns
        --------
        int
        '''
        return len(self.pessoas)

    def __str__(self):
        '''Representação em string do objeto.
        
        Returns
        -------
        str
        '''
        return ('Pessoas: {}\n' 'Pessoas confirmadas: {}'
                .format(len(self), self.pessoas_confirmadas))
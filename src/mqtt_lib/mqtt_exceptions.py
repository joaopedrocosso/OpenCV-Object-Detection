class ConeccaoError(Exception):
    '''Quando não se consegue conectar com um broker.'''
    def __init__(self, mensagem, *args, **kwargs):
        super().__init__(mensagem, *args, **kwargs)
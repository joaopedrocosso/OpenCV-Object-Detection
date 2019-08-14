from paho.mqtt import publish

class MQTTPublisher:

    '''Envia uma mensagem para um servidor mqtt.

    Parameters
    ----------
    hostname : str
        O endereço do broker ao qual se deseja conectar.
    porta : int
        A porta à qual se quer conectar.
    username : str
        Nome de usuário.
    password : str
        Senha.
    '''

    def __init__(self, hostname, porta, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.porta = porta
        self.topicos = set()
    
    def publish(self, mensagem, qos=0):
        '''Publica uma mensagem nos tópicos cadastrados.

        Parameters
        -----------
        mensagem : int, str
            Uma mensagem qualquer; será enviado para um ou mais tópicos 
            mqtt.
        qos : {0, 1, 2}, optional
            Qualidade de serviço.
        '''
        auth = {'username':self.username, 'password':self.password}
        for topico in self.topicos:
            publish.single(topico, mensagem, hostname=self.hostname, qos=0, auth=auth, port=self.porta)
    
    def esvazia_topicos(self):
        '''Esvazia o registro de tópicos.'''
        self.topicos = set()

    def adicionar_topico(self, topico):
        '''Adiciona um tópico ao qual a mensagem será publicada.

        Parameters
        ----------
        topico : str
            O tópico que se deseja adicionar.
        '''
        self.topicos.add(topico)
    
    def remove_topico(self, topico):
        '''Remove um tópico dos tópicos a serem usados.

        Parameters
        -----------
        topico : str
            Tópico a ser removido.
        '''
        self.topicos.remove(topico)
    


    
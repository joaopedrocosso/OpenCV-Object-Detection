from paho.mqtt.client import Client

def dummy(*args, **kwargs):
    pass

class MQTTClient:

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

    def __init__(self, hostname, porta, username, password, on_message=dummy, 
                 on_connect=dummy, on_subscribe=dummy):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.porta = porta

        self.cliente = Client()
        self.cliente.on_message = on_message
        self.cliente.on_connect = on_connect

    def conectar(self):
        self.cliente.username_pw_set(username=self.username, password=self.password)
        self.cliente.connect(self.hostname, self.porta)
        self.cliente.loop_forever()
    
    def desconectar(self):
        self.cliente.disconnect()
    
    def esvazia_topicos(self):
        '''Esvazia o registro de tópicos.'''
        self.topicos = set()

    def adicionar_topico(self, topico, qos=0):
        '''Adiciona um tópico ao qual a mensagem será publicada.

        Parameters
        ----------
        topico : str
            O tópico que se deseja adicionar.
        qos : int, optional
            Qualidade de serviço. (Padrão=0)
        '''
        self.cliente.subscribe(topico, qos)
    
    def remove_topico(self, topico):
        '''Remove um tópico dos tópicos a serem usados.

        Parameters
        -----------
        topico : str
            Tópico a ser removido.
        '''
        self.cliente.unsubscribe(topico)
    


    
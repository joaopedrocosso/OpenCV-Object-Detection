import cmd

class HelloWorld(cmd.Cmd):

    prompt = '>> '
    def do_novo(self, line):
        itens = line.split()
        
    
    def do_EOF(self, line):
        return True
    
    def postloop(self):
        print()
    
    def do_exit(self, line):
        return True

def identifica_argumentos(args):
    
    valores_iniciais = []
    comandos_e_argumentos = dict()
    comando_anterior = ''
    for arg in args:
        if not e_comando(arg):
            if comando_anterior == '':
                valores_iniciais.append(arg)
            else:
                comandos_e_argumentos[comando_anterior].append(arg)
        else:
            comandos_e_argumentos[arg] = []
            comando_anterior = arg

    return valores_iniciais, comandos_e_argumentos

def e_comando(s):
    return s.startswith('-')
    
if __name__ == '__main__':

    print(identifica_argumentos('4   5 3 --ge s -t sdf -o 33'))
    #HelloWorld().cmdloop()
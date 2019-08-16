import os

src_folder = '../src'
extras_folder = '../../detector-itens'

def executa_demo(comandos_extras=''):
    os.system('export PYTHONPATH=${PYTHONPATH}:'+src_folder)
    string_runner = "python3 {src_folder}/runner.py --modelo-yolo " \
                    "{extras_folder}/modelo-yolo --mostrar-video --mostrar-caixas " \
                    "--tempo-atualizacao-json 5 "+comandos_extras
    os.system(string_runner.format(src_folder=src_folder, extras_folder=extras_folder))
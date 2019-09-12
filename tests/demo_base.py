import os

src_folder = '../src'
extras_folder = '../../detector-itens'
runner_path = src_folder+'/runner.py'

def executa_demo(comandos_extras=''):
    os.system('export PYTHONPATH=${PYTHONPATH}:'+src_folder)
    string_runner = (
        'python3 {runner_path} --modelo-yolo {extras_folder}/modelo-yolo '
        '--mostrar-video --mostrar-caixas --tempo-atualizacao-resultados 5'
        .format(src_folder=src_folder, extras_folder=extras_folder,
                runner_path=runner_path)
    )
    string_runner += ' '+comandos_extras
    
    os.system(string_runner)
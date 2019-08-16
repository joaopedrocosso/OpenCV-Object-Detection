import sys
from demo_base import executa_demo

video_nome = '01.mp4'
if len(sys.argv) > 1:
    video_nome = sys.argv[1]

executa_demo('--arquivo-video {extras_folder}/videos/'+video_nome)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../src')

from imagelib import ktools
from videolib.webcamVideoStream import WebcamVideoStream

channel = 1
max_largura = 700
if len(sys.argv) >= 2:
    channel = sys.argv[1]
if len(sys.argv) >= 3:
    try:
        max_largura = int(sys.argv[2])
    except ValueError:
        sys.exit('usage: python3 '+__file__+' [canal, [largura-máxima]]')

link = 'rtsp://LCC:6023-FL%40b@152.92.234.55:554/h264/ch{channel}/main/av_stream'.format(channel=channel)

vs = WebcamVideoStream(link).start()

while not vs.stopped:
    try:
        frame = vs.read()
    except:
        break
    frame = ktools.resize(frame, max_largura)
    k = ktools.show_image(frame, title='DVR', wait_time=1, close_window=False)
    if chr(k) == 'q':
        break

ktools.destroy_all_windows()
vs.stop()
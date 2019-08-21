from imagelib import ktools
from videolib.webcamVideoStream import WebcamVideoStream

link = 'rtsp://LCC:6023-FL%40b@152.92.234.55:554/h264/ch{channel}/main/av_stream'.format(channel=8)

vs = WebcamVideoStream(link).start()

while not vs.stopped:
    try:
        frame = vs.read()
    except:
        break
    k = ktools.show_image(frame, title='DVR', wait_time=1, close_window=False)
    if chr(k) == 'q':
        break

ktools.destroy_all_windows()
vs.stop()
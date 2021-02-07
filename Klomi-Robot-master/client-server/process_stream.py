import requests
import os
from sys import argv
import subprocess
import time
import signal
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer
from threading import Thread

server = argv[1]
status_stream = server +'/record/status'
stream = server + '/stream.mjpg'
send_processed = server + '/record/processed'

CURL = ['curl',stream]
FFMPEG = 'ffmpeg -y -f mjpeg -i - -f mp4 tmp.mp4'.split()
THUMB_TMPL = ('ffmpeg -y -i videos/{idx}.mp4 -vf "select=eq(n\,0)"'
        ' -vf scale=320:-2 -q:v 3 videos/{idx}.jpg')

def thumbnail(idx):
    subprocess.call(THUMB_TMPL.format(idx=idx).split())

def ffmpeg_file(fname):
    FFMPEG[-1] = os.path.join('videos',fname)
    return FFMPEG

def _iter_lines(response):
    resp_line = b''
    for chunk in response.iter_content():
        resp_line += chunk
        if b'\n' in chunk:
            yield resp_line
            resp_line = b''

# fork an http.server 
httpd = HTTPServer(('0.0.0.0',8000),SimpleHTTPRequestHandler)
server_thread = Thread(target = httpd.serve_forever,daemon=True)
server_thread.start()

with requests.get(status_stream, stream=True) as r:
    ffmpeg = None
    record_count = 0
    for line in _iter_lines(r):
        streaming = line.strip().decode('ascii')
        streaming = streaming == 'True'
        if streaming and ffmpeg is None:
            fname = '{}.mp4'.format(record_count)
            curl = subprocess.Popen(CURL,stdout=subprocess.PIPE)
            ffmpeg = subprocess.Popen(ffmpeg_file(fname),stdin=curl.stdout)
        elif not streaming and ffmpeg is not None:
            ffmpeg.terminate()
            curl.terminate()
            ffmpeg = None
            time.sleep(0.5)
            thumbnail(record_count)
            record_count += 1


# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition, Thread
from queue import Queue
from http import server
import RPi.GPIO as GPIO
import time
import subprocess

TILT_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

PAGE="""\

<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
  </head>
  <body>
  <h1>The Klomi Cam</h1>
  <div> <img width="100%" src="/stream.mjpg"/> </div>
  <iframe hidden name="hiddenFrame" ></iframe>
  <form action="/setmovemode" method="get" target="hiddenFrame">
    <button type="submit" name="following" value="true">Follow Me</button>
    <button type="submit" name="following" value="false">Don't Follow Me</button>
  </form>
  <form action="/playsong" method="get" target="hiddenFrame">
    <input type="text" name="song">
    <button type="submit" value="Submit">Inspire Me!</button>
  </form>
  </body>
</html>
"""

class ServoController(Thread):
    ZERO = 4
    ONE_EIGHTY = 11
    def __init__(self, pin):
        super().__init__()
        self.daemon=True
        self.NINETY = (self.ZERO + self.ONE_EIGHTY)/2.
        self.pin = pin
        self.duty_cycle = self.NINETY
        GPIO.setup(self.pin,GPIO.OUT)
        self.tQ = Queue()
        self._found_something = False
        self._direction = None

    def setCycle(self,duty_cycle):
        if duty_cycle < self.ZERO:
            duty_cycle = self.ZERO
        if duty_cycle > self.ONE_EIGHTY:
            duty_cycle = self.ONE_EIGHTY

        tilt = GPIO.PWM(self.pin,50.0)
        tilt.start(8)
        tilt.ChangeDutyCycle(duty_cycle)
        time.sleep(.01)
        tilt.stop()


    def move_towards(self,point):
        """ Point should be normalized """
        if isinstance(point, tuple):
            self._found_something = True
            x, y = point
            if x < 1/6:
                self._direction = 'Left'
                self.duty_cycle += .2
                self.setCycle(self.duty_cycle)
            elif x < 1/3:
                self._direction = 'Left'
                self.duty_cycle += .1
                self.setCycle(self.duty_cycle)
            elif x > 2/3:
                self._direction = 'Right'
                self.duty_cycle -= .1
                self.setCycle(self.duty_cycle)
            elif x > 5/6:
                self._direction = 'Right'
                self.duty_cycle -= .2
                self.setCycle(self.duty_cycle)
        elif self._found_something and self._direction:
            if self._direction == 'Left':
                self.duty_cycle += .4
                self.setCycle(self.duty_cycle)
                if self.duty_cycle > self.ONE_EIGHTY:
                    self._direction = 'Right'
            elif self._direction == 'Right':
                self.duty_cycle -= .4
                self.setCycle(self.duty_cycle)
                if self.duty_cycle < self.ZERO:
                    self._direction = 'Left'

    def run(self):
        while 1:
            point = self.tQ.get()
            self.move_towards(point)

SERVOS = ServoController(TILT_PIN)

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):

    def pointat(self):
        args = self.path.split('?')[1]
        args = args.split('&')
        arg_dict = {a.split('=')[0]:a.split('=')[1] for a in args}
        SERVOS.tQ.put((float(arg_dict['x']),float(arg_dict['y'])))

    def send_ok(self):
        content = "OK".encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def playsong(self):
        args = self.path.split('?')[1]
        song = args.split('=')[1].replace('+', ' ')
        play_args = ['../get_soundcloud_song.sh',song]
        print(play_args)
        subprocess.Popen(play_args) 

    def songctl(self):
        args = self.path.split('?')[1]
        song = args.split('=')[1].replace('+', ' ')
        play_args = ['mpc', '-p', '6681', song]
        print(play_args)
        subprocess.Popen(play_args) 

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            with open('index.html','r') as indexf:
                content = indexf.read().encode('utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path.startswith('/pointat'):
            self.pointat()
            self.send_ok()
        elif self.path.startswith('/keeplooking'):
            SERVOS.tQ.put(None)
            self.send_ok()
        elif self.path.startswith('/setmovemode'):
            self.setmovemode()
            self.send_ok()
        elif self.path.startswith('/playsong'):
            self.playsong()
            self.send_ok()
        elif self.path.startswith('/songctl'):
            self.songctl()
            self.send_ok()
        else:
            print(self.path)
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    SERVOS.start()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 80)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()


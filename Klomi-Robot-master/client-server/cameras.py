import io
import picamera
from threading import Condition
from contextlib import contextmanager
@contextmanager
def camera_context():
    global cam_output
    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        cam_output = StreamingOutput()
        camera.start_recording(cam_output, format='mjpeg')
        try:
            yield
        finally:
            camera.stop_recording()

cam_output = None
def frame_generator():
    while 1:
        with cam_output.condition:
            cam_output.condition.wait()
            frame = cam_output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n')


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

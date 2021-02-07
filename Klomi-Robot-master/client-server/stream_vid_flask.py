from servos import Servos
from cameras import camera_context, frame_generator
from flask import Flask, Response, request, send_from_directory
app = Flask(__name__)

@app.route('/index.html',methods=['GET'])
def index():
    return send_from_directory('.','index.html')

@app.route('/stream.mjpg',methods=['GET'])
def stream():
    return Response(frame_generator(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

with camera_context():
    Servos.start()
    app.run(host='0.0.0.0',port=8000)

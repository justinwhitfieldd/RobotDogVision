from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import io
from PIL import Image
import base64, cv2
import numpy as np
import pyshine as ps
from flask_cors import CORS, cross_origin
import imutils
import dlib
from engineio.payload import Payload

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
Payload.max_decode_packets = 2048

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

def readb64(base64_string):
    idx = base64_string.find('base64,')
    base64_string  = base64_string[idx+7:]
    sbuf = io.BytesIO()
    sbuf.write(base64.b64decode(base64_string, ' /'))
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

@socketio.on('image')
def image(data_image):
    frame = readb64(data_image)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    coordinates = []

    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()
        coordinates.append({"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1})
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

    imgencode = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])[1]
    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpeg;base64,'
    stringData = b64_src + stringData

    emit('response_back', {"image": stringData, "coordinates": coordinates})

if __name__ == '__main__':
    socketio.run(app, port=9990, debug=True)

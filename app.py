from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
import tensorflow as tf
import tensorflow_hub as hub
import time
import io
import cv2
import base64
import numpy as np
from PIL import Image
import requests
from engineio.payload import Payload
# Define body connections
import math
body_parts = {
    0: "nose",
    1: "leftEye",
    2: "rightEye",
    3: "leftEar",
    4: "rightEar",
    5: "leftShoulder",
    6: "rightShoulder",
    7: "leftElbow",
    8: "rightElbow",
    9: "leftWrist",
    10: "rightWrist",
    11: "leftHip",
    12: "rightHip",
    13: "leftKnee",
    14: "rightKnee",
    15: "leftAnkle",
    16: "rightAnkle"
}

body_connections = [
    (0, 1), #nose left eye 0
  #  (1, 3), left eye, left ear
    (0, 2), #nose right eye 1
    (1,2),  #2
   # (2, 4),  # right eye right ear
    (5, 7), #3
    (7, 9),  # Left arm 4
    (6, 8),  #5
    (8, 10),  # Right arm 6
    (5, 6),  # Shoulders7
    (5, 11),  # 8
    (6, 12),  # Body 9
    (11, 13), # 10
    (11, 12), #11
    (13, 15),  # Left leg12
    (12, 14), #13
    (14, 16)  # Right leg 14
]
# Initialize MoveNet model
model = hub.load("https://tfhub.dev/google/movenet/multipose/lightning/1")
movenet = model.signatures['serving_default']

Payload.max_decode_packets = 2048

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')
@app.route('/output', methods=['POST', 'GET'])
def output():
    return render_template('output.html')

def readb64(base64_string):
    idx = base64_string.find('base64,')
    base64_string  = base64_string[idx+7:]
    sbuf = io.BytesIO()
    sbuf.write(base64.b64decode(base64_string, ' /'))
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)
def calculate_distance(point1, point2):
    return int(np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2))

def determine_intensity_duration(distance):
    intensity = min(1, distance * 0.01)  # scale as needed, ensuring intensity <= 1
    duration = min(5000, distance * 10)   # scale as needed, duration in milliseconds
    return intensity, duration

@socketio.on('image')
def image(data_image):
    frame = readb64(data_image)
    
    # Process pose detection
    input_image = cv2.resize(frame, (256, 256))
    input_image = tf.expand_dims(input_image, axis=0)
    input_image = tf.cast(input_image, dtype=tf.int32)
    
    outputs = movenet(input_image)
    keypoints = outputs['output_0'].numpy()[0]
    
    # Draw keypoints and connections
    for person_id in range(1):
        keypoints_for_person = keypoints[person_id]
        
        points = {}
        
        for i in range(0, 51, 3):
            y, x, score = keypoints_for_person[i:i + 3]
            point_id = i // 3
            
            if score > 0.3:  # confidence score
                x = int(x * frame.shape[1])
                y = int(y * frame.shape[0])
                
                points[point_id] = (x, y)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        # Draw connections
        for start_point, end_point in body_connections:
            if start_point in points and end_point in points:
                cv2.line(frame, points[start_point], points[end_point], (255, 0, 0), 2)


        # Draw the central point
        if all(key in points for key in [5, 6, 11, 12]):
            center_x = (points[5][0] + points[6][0] + points[11][0] + points[12][0]) // 4
            center_y = (points[5][1] + points[6][1] + points[11][1] + points[12][1]) // 4
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            image_center = (128, 128)
            distance = calculate_distance((center_x, center_y), image_center)
            intensity, duration = determine_intensity_duration(distance)

            if center_x < 128:
                print("move right")
                send_command("right", intensity, duration)
            if center_x > 128:
                print("move left")
                send_command("left", intensity, duration)
            if center_y < 128:
                print("move up")
                send_command("up", intensity, duration)
            if center_y > 128:
                print("move down")
                send_command("down", intensity, duration)
                
    # Encode frame back to base64 string
    imgencode = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])[1]
    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpeg;base64,'
    stringData = b64_src + stringData
    socketio.emit('response_back', stringData, broadcast=True)

# @app.route('/send_command', methods=['POST'])
# def send_command(direction):
#     if direction == "up":
#         requests.post('http://localhost:3000/receive_command', json={'command': 'up'})
#     if direction == "down":
#         requests.post('http://localhost:3000/receive_command', json={'command': 'down'})
#     if direction == "left":
#         requests.post('http://localhost:3000/receive_command', json={'command': 'left'})
#     if direction == "right":
#         requests.post('http://localhost:3000/receive_command', json={'command': 'right'})     

@app.route('/send_command', methods=['POST'])
def send_command(direction, intensity, duration):
    requests.post('http://localhost:3000/receive_command', json={'command': direction, 'intensity': intensity, 'duration': duration})
if __name__ == '__main__':
    socketio.run(app, port=5001, debug=True)

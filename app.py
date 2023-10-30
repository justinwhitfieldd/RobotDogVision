from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import io
from PIL import Image
import base64,cv2
import numpy as np
import pyshine as ps
from flask_cors import CORS,cross_origin
import imutils
import dlib
from engineio.payload import Payload
from keras.layers import LSTM

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
Payload.max_decode_packets = 2048

app = Flask(__name__)
socketio = SocketIO(app,cors_allowed_origins='*' )



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

def moving_average(x):
    return np.mean(x)


@socketio.on('catch-frame')
def catch_frame(data):

    emit('response_back', data)  


global fps,prev_recv_time,cnt,fps_array
fps=30
prev_recv_time = 0
cnt=0
fps_array=[0]

@socketio.on('image')
def image(data_image):
    frame = readb64(data_image)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

    imgencode = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])[1]
    stringData = base64.b64encode(imgencode).decode('utf-8')
    b64_src = 'data:image/jpeg;base64,'
    stringData = b64_src + stringData
    emit('response_back', stringData)




def getMaskOfLips(img,points):
    """ This function will input the lips points and the image
        It will return the mask of lips region containing white pixels
    """
    mask = np.zeros_like(img)
    mask = cv2.fillPoly(mask,[points],(255,255,255))
    return mask 


def changeLipstick(img,value):
    """ This funciton will take img image and lipstick color RGB
        Out the image with a changed lip color of the image
    """ 

    img = cv2.resize(img,(0,0),None,1,1)
    imgOriginal = img.copy()
    imgColorLips=imgOriginal
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(imgGray)

    for face in faces:
        x1,y1 = face.left(),face.top()
        x2,y2 = face.right(),face.bottom()
       
        facial_landmarks = predictor(imgGray,face)
        points =[]
        for i in range(68):
            x = facial_landmarks.part(i).x
            y = facial_landmarks.part(i).y
            points.append([x,y])


        points = np.array(points)
        imgLips = getMaskOfLips(img,points[48:61])
        
        imgColorLips = np.zeros_like(imgLips)
        
        imgColorLips[:] =value[2],value[1],value[0]
        imgColorLips = cv2.bitwise_and(imgLips,imgColorLips)
        
        value = 1
        value=value//10
        if value%2==0:
            value+=1
        kernel_size = (6+value,6+value) # +1 is to avoid 0
        
        weight = 1
        weight = 0.4 + (weight)/400
        imgColorLips = cv2.GaussianBlur(imgColorLips,kernel_size,10)
        imgColorLips = cv2.addWeighted(imgOriginal,1,imgColorLips,weight,0)
        
        
        
    return imgColorLips


if __name__ == '__main__':
    socketio.run(app,port=9990 ,debug=True)
   


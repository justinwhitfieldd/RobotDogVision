import socketio
import cv2
import numpy as np
import base64
import threading
import time

frame = None
stop_thread = False

def show_frames():
    global frame, stop_thread
    while not stop_thread:
        if frame is not None:
            cv2.imshow("Server View", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        time.sleep(0.03)  # introduce delay to limit frame rate
    cv2.destroyAllWindows()

cv2.namedWindow("Server View", cv2.WINDOW_NORMAL)

sio = socketio.Client()

@sio.on('server_image')
def on_message(data):
    global frame
    # Decode base64 image
    idx = data.find('base64,')
    data = data[idx+7:]
    nparr = np.frombuffer(base64.b64decode(data), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

sio.connect('http://localhost:5001')

# Start thread to show frames
thread = threading.Thread(target=show_frames)
thread.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_thread = True
    thread.join()
    sio.disconnect()

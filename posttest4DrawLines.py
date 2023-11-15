import cv2
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)

# Load the model
model = hub.load("https://tfhub.dev/google/movenet/multipose/lightning/1")
movenet = model.signatures['serving_default']

# Define body connections
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
    (0, 1), #nose left eye
  #  (1, 3), left eye, left ear
    (0, 2), #nose right eye
    (1,2),
   # (2, 4),  # right eye right ear
    (5, 7), 
    (7, 9),  # Left arm
    (6, 8), 
    (8, 10),  # Right arm
    (5, 6),  # Shoulders
    (5, 11), 
    (6, 12),  # Body
    (11, 13), 
    (11, 12),
    (13, 15),  # Left leg
    (12, 14), 
    (14, 16)  # Right leg
]

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    input_image = cv2.resize(frame, (256, 256))
    input_image = tf.expand_dims(input_image, axis=0)
    input_image = tf.cast(input_image, dtype=tf.int32)

    # Run inference
    outputs = movenet(input_image)
    keypoints = outputs['output_0'].numpy()[0]

    # Iterate over all detected bodies (up to 6)
    for person_id in range(6):
        keypoints_for_person = keypoints[person_id]
        
        points = {}
        
        # Extract keypoints
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

    cv2.imshow('MoveNet MultiPose', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

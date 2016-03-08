# http://stackoverflow.com/questions/35459719/no-webcam-stream-when-embedding-webrtc-in-flask-app
from flask import Flask, render_template
from flask_socketio import SocketIO
import numpy as np

import base64
import cv2
import os
import shutil
from distutils import dir_util
import glob
import skimage.io
import skimage.color
import skimage.io
import skimage.transform

# local API
from services import FaceCropper
from services import EmotionFeatures
from services import SVMClassifierAPI


svm_emo_landmarks_detector = "./static/resources/svm_emo_landmarks_detector/emotion_detector_svm_model_landmarks_features_3.pkl"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

labels = {0: 'Neutral', 1: 'Happy', 2: 'Sad', 3: 'Surprise', 4: 'Angry', 5: 'Disgust', 6: 'Fear'}

faceCropper = FaceCropper(NEW_IMAGE_SIZE = (100, 100))
emotionFeatures = EmotionFeatures()
svmClassifierAPI = SVMClassifierAPI(svm_emo_landmarks_detector)

# app.debug = True

@app.route('/')
def home():
  return render_template('index.html')

@socketio.on("frame")
def handle_frame(frame):
  # print '\n =============== \n'
  # print 'received frame ' + frame
  # print '\n =============== \n'
  
  if not isinstance(frame, basestring):
    return
  
  image_ref = 'null'
  
  try:
    image_ref = frame.split(',')[1]
  except IndexError:
    image_ref = "null"
  
  if image_ref != "null":
    image = base64.b64decode(image_ref)
    image = np.fromstring(image, dtype=np.uint8)
    image = cv2.imdecode(image, 1)
    cropped_image, success_flag = faceCropper.process_single_image_cv2(image, NEW_IMAGE_SIZE = (100, 100))
    cropped_image = cropped_image.reshape(100, 100).astype('uint8')
    if success_flag:
      # take image
      face_landmarks = emotionFeatures.get_landmarks_for_single_image(cropped_image).flatten()
      face_landmarks = face_landmarks.reshape(1, -1)
      prediction = svmClassifierAPI.predict(face_landmarks)
      print 'You are ', labels.get(prediction[0])
    else:
      print 'skipped frame..'
    
  
  
  
      
if __name__ == '__main__':
    socketio.run(app)

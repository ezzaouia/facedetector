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

class FaceCropper(object):
    
    def __init__(self, dataset_path=None, NEW_IMAGE_SIZE = (100, 100)):
        self.dataset_path = dataset_path
        self.NEW_IMAGE_SIZE = NEW_IMAGE_SIZE
        # labels = {'Neutral': 0, 'Happy': 1, 'Sad': 2, 'Surprise': 3, 'Angry': 4, 'Disgust': 5, 'Fear': 6}
        self.labelsDict = {'NE': 0, 'HA': 1, 'SA': 2, 'SU': 3, 'AN': 4, 'DI': 5, 'FE': 6, 'CO': 7}
    
    def write_list_to_file(self, file_path, item_list):
        f = open(file_path, 'wb')
        for item in item_list:
            f.write(item + '\n')
        f.close
    
    def cropper_lift(self):
        return self.crop_and_align_all_faces(self.dataset_path)
    
    def crop_and_align_all_faces(self, dataset_path):
        cropped_images = []
        labels = []
        images_extensions = ['*.png', '*.tiff']
        all_images_paths = sorted([x for y in images_extensions for x in glob.glob(os.path.join(dataset_path, y))])
        track_process_issues = [] 
        
        for image_file_path in all_images_paths:
            numpy_img, success_flag = self.process_single_image(image_file_path, self.NEW_IMAGE_SIZE)
            
            # add the images issued in processing
            if not success_flag:
                track_process_issues.append(image_file_path)
            else:
                image_label_nbr = int(self.labelsDict.get(os.path.split(image_file_path)[1].split(".")[1][:2]))
                labels.append(image_label_nbr)
                cropped_images.append(numpy_img) 
        
        if len(track_process_issues) > 0:
            self.write_list_to_file(os.path.join(dataset_path, 'images_issued.txt'), track_process_issues)
            
        return np.vstack(cropped_images), np.array(labels)
                
    def process_single_image(self, image_file_path, NEW_IMAGE_SIZE):
        # read the image as numpy array
        Image = cv2.imread(image_file_path)
        Image = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    
        # detect face and crop it
        Image_croped, success_flag = self.detect_and_crop_face(Image)
        # if face is successfuly detected
        # align it in 
        if success_flag:
            Image_croped = cv2.resize(Image_croped, NEW_IMAGE_SIZE)
        
        Image_croped = np.array(Image_croped, 'f')
        Image_croped = Image_croped.flatten()
        
        return Image_croped, success_flag
    
    def process_single_image_cv2(self, cv2_encoded_image, NEW_IMAGE_SIZE):
        # read the image as numpy array
        # Image = cv2.imread(image_file_path)
        Image = cv2.cvtColor(cv2_encoded_image, cv2.COLOR_BGR2GRAY)
    
        # detect face and crop it
        Image_croped, success_flag = self.detect_and_crop_face(Image)
        # if face is successfuly detected
        # align it in 
        if success_flag:
            Image_croped = cv2.resize(Image_croped, NEW_IMAGE_SIZE)
        
        Image_croped = np.array(Image_croped, 'f')
        Image_croped = Image_croped.flatten()
        
        return Image_croped, success_flag
        
    def detect_and_crop_face(self, Image):
        success_flag = False
        face_detector = FaceDetector(scale_factor=1.3, min_neighbors=5,
                                     min_size_scalar=0.5, max_size_scalar=0.8)
        faces = face_detector.detect_faces(Image)
        
        if len(faces) == 0:
            # Try with more lenient conditions
            face_detector = FaceDetector(scale_factor=1.3,
                                         min_neighbors=3,
                                         min_size_scalar=0.5,
                                         max_size_scalar=0.8)
            
            faces = face_detector.detect_faces(Image)
        
        if len(faces) == 0:
            # Try with more lenient conditions
            face_detector = FaceDetector(scale_factor=1.1,
                                         min_neighbors=3)
            
            faces = face_detector.detect_faces(Image)
            
            
            if len(faces) == 0:
                print 'Missed the face!'
                return Image, success_flag
        
        success_flag = True
        Image_croped = face_detector.crop_face(Image, faces[0])
        
        return Image_croped, success_flag
    

class FaceDetector(object):
    
    def __init__(self, scale_factor=1.3, min_neighbors=5,
                 min_size_scalar=0.25, max_size_scalar=0.75):
        
        module_path = os.path.split(os.path.dirname(os.path.realpath('__file__')))[0]
        classifier_path = os.path.join(module_path, 'facedetector/static/resources',
                                       'haarcascade_frontalface_default.xml') 
        self.detector = cv2.CascadeClassifier(classifier_path)
        if self.detector.empty():
            print classifier_path
            raise Exception('Classifier xml file was not found.')
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size_scalar = min_size_scalar
        self.max_size_scalar = max_size_scalar
        # print self.detector

    def detect_faces(self, Image):
        height, width = Image.shape
        min_dim = np.min([height, width])
        min_size = (int(min_dim*self.min_size_scalar),
                    int(min_dim*self.min_size_scalar))
        max_size = (int(min_dim*self.max_size_scalar),
                    int(min_dim*self.max_size_scalar))

        faces = self.detector.detectMultiScale(Image, self.scale_factor,
                                               self.min_neighbors, 0,
                                               min_size,
                                               max_size)
        return faces

    def crop_face(self, Image, face):
        (x, y, w, h) = face
        Image_croped = Image[y:y+h, x:x+w]
        return Image_croped
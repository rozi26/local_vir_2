import sys
sys.path.append("\\".join(str(__file__).split("\\")[:-2] + ['assets']))
import numpy as np
import argparse
import imutils
import dlib
import cv2
import mediapipe as mp
from imutils import face_utils

ASSESTS_PATH = "\\".join(str(__file__).split("\\")[:-2] + ['assets'])

class Models:
    def __init__(self) -> None:
        self.face_detecror = None
        self.dots_predictor = None

    def get_face_detector(self):
        if (self.face_detecror is None): self.face_detecror = dlib.get_frontal_face_detector()
        return self.face_detecror
    
    def get_dots_predictor(self):
        if (self.dots_predictor is None): self.dots_predictor =  dlib.shape_predictor(ASSESTS_PATH + "\\shape_predictor_68_face_landmarks.dat")
        return self.dots_predictor


MODELS = Models()

def find_faces(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    return MODELS.get_face_detector()(gray,1)

def find_faces_dots1(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    faces = MODELS.get_face_detector()(gray,1)
    if (len(faces) == 0): return np.zeros(0)
    dots = face_utils.shape_to_np(MODELS.get_dots_predictor()(gray,faces[0]))
    for face in faces: cv2.rectangle(img,(face.left(),face.top()),(face.right(), face.bottom()),[255,0,0],3)
    return dots

def find_faces_dots2(img):
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=ASSESTS_PATH + "\\face_landmarker.task"),
        running_mode=VisionRunningMode.IMAGE)
    
    with FaceLandmarker.create_from_options(options) as landmarker:
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        return landmarker.detect(img)
if (__name__ == "__main__"):
    cam = cv2.VideoCapture(0)

    while (True):
        ret , frame = cam.read()
        dots = find_faces_dots1(frame)
        print(dots)
        for r in dots:
            cv2.circle(frame,r,2,(0,255,0))
            #cv2.rectangle(frame,(r.left(),r.top()),(r.right(),r.bottom()),[0,255,0],4)
        cv2.imshow("fr",frame)
        if (cv2.waitKey(1) & 0xFF == ord('q')): break
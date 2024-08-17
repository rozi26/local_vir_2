import cv2
import numpy as np
import mediapipe as mp
import math
import utils as ut
from scipy.ndimage import rotate
from matplotlib import pyplot as plt
from PIL import Image


CV2_PATH = r"C:\Users\iddor\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\site-packages\cv2\data"

class Anonimaitor():
    def __init__(self, bg_path, mask_path) -> None:
        self.face_cascade = cv2.CascadeClassifier(CV2_PATH + '\haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(CV2_PATH + '\haarcascade_eye_tree_eyeglasses.xml')
        self.bg_path = bg_path
        self.mask_path = mask_path
        self.first = True
        self.eyes = None
    
    def anonimaite(self,img):
        if (self.first):
            self.bg = np.array(cv2.resize(cv2.imread(self.bg_path),img.shape[:2][::-1]))
            self.mask = np.array(Image.open(self.mask_path))
            self.mask_eyes = np.argwhere(np.all(self.mask == [255,0,0,255], axis=-1))
            self.mask_eyes_dif = math.sqrt((self.mask_eyes[0,0]-self.mask_eyes[1,0])**2+(self.mask_eyes[0,1]-self.mask_eyes[1,1])**2)
            self.first_eye_center_dif = math.sqrt((self.mask_eyes[0,0]-len(self.mask)//2)**2 + (self.mask_eyes[0,1]-len(self.mask[0])//2)**2)
            self.first = False

        mask = getBackgroundMask(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 4)
        eyes = self.eyes
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            face_eyes = self.eye_cascade.detectMultiScale(roi_gray)
            if (len(face_eyes) == 2):
                eyes = face_eyes
                for e in eyes:
                    e[0] += x; e[1] += y
                self.eyes = eyes
                break
        if (eyes is None):
            condition = np.stack(mask,axis=-1) > 0.5
            condition = np.swapaxes(condition,0,1)
            condition = np.reshape(condition,(condition.shape + (1,)))
            shadow = np.zeros(img.shape,dtype=np.uint8)
            img = np.where(condition,shadow,self.bg)
        else:
            ps = [(ey[0]+ey[2]//2,ey[1]+ey[3]//2) for ey in eyes]
            cv2.circle(img,ps[0],5,[0,255,0],5)
            cv2.circle(img,ps[1],5,[0,255,0],5)
            dx,dy = ps[1][0]-ps[0][0], ps[1][1] - ps[0][1]
            eyes_dif = math.sqrt(dx*dx + dy*dy)
            eyes_ratio = eyes_dif/self.mask_eyes_dif
            temp_mask = cv2.resize(self.mask,(round(len(self.mask)*eyes_ratio),round(len(self.mask[0])*eyes_ratio)))
            engale = math.atan2(dy,dx)
            degress = engale*180/math.pi
            
            
            print("engale is " + str(degress))
            temp_mask = rotate(temp_mask,degress)
            
            put_point = (100,100)
            cond = np.zeros(self.bg.shape[:2],dtype=np.uint)
            lx = min(len(img[0])-put_point[1],len(temp_mask[0]))
            ly = min(len(img)-put_point[0],len(temp_mask))
            cond[put_point[0]:put_point[0]+ly,put_point[1]:put_point[1]+lx] = temp_mask[:ly,:lx,3] == 255
            #img = np.where(cond,img,self.bg)    
            for i1,y in enumerate(img):
                for i2, x in enumerate(y):
                    x[:] = cond[i1][i2]*255
                        
            #print(f"mask shape: {self.mask.shape}")
            print(temp_mask.shape)
            
        return img

class Anonimaitor2():
    def __init__(self, bg_path, mask_path) -> None:
        self.face_cascade = None
        self.eye_cascade = cv2.CascadeClassifier(CV2_PATH + '\haarcascade_eye_tree_eyeglasses.xml')
        self.bg_path = bg_path
        self.mask_path = mask_path
        self.eyes_from_face = True
        self.first = True
        
        #for recorve
        self.rec_eyes = None
        self.rec_frames_without_eyes = 0 
    
    def get_unconnected_image(self,code=-1):
        return self.bg
    
    def find_faces(self,img):
        if (self.face_cascade is None):
            self.face_cascade = cv2.CascadeClassifier(CV2_PATH + '\haarcascade_frontalface_default.xml')
        return self.face_cascade.detectMultiScale(img,1.3,4)
    
    def find_eyes(self, img):
        eyes = self.eye_cascade.detectMultiScale(img,1.3,1)
        if (len(eyes) == 2): 
            self.rec_eyes = eyes
            self.rec_frames_without_eyes = 0
            return eyes
        if (self.rec_frames_without_eyes > 10 or self.rec_eyes is None): return []
        self.rec_frames_without_eyes += 1
        return self.rec_eyes
    
    def anonimaite(self,img):
        if (self.first):
            self.bg = np.array(cv2.resize(cv2.imread(self.bg_path),img.shape[:2][::-1]))
            self.bg = cv2.cvtColor(self.bg, cv2.COLOR_BGR2BGRA)
            self.mask = np.array(Image.open(self.mask_path))
            self.mask_eyes = np.argwhere(np.all(self.mask == [255,0,0,255], axis=-1))
            self.mask_eyes_dif = math.sqrt((self.mask_eyes[0,0]-self.mask_eyes[1,0])**2+(self.mask_eyes[0,1]-self.mask_eyes[1,1])**2)
            self.first = False
        
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
        
        if (self.eyes_from_face):
            faces = self.find_faces(gray)
            #for face in faces: cv2.rectangle(img,(face[0],face[1]),(face[0]+face[2],face[1]+face[3]),[0,255,0])
            if (len(faces) == 0): return self.get_unconnected_image(1)
            face = max(faces,key=lambda x: x[2]*x[3])
            cv2.rectangle(img,(face[0],face[1]),(face[0]+face[2],face[1]+face[3]),[0,255,0])
            eyes = self.find_eyes(gray[face[0]:face[0]+face[2],face[1]:face[1]+face[2]])
            eyes = [[eye[0]+face[1],eye[1]+face[0],eye[2],eye[3]] for eye in eyes]
        else: eyes = self.find_eyes(gray)
        for eye in eyes: cv2.rectangle(img,(eye[0],eye[1]),(eye[0]+eye[2],eye[1]+eye[3]),[0,0,255])
        
        if (len(eyes) != 2): return self.get_unconnected_image(2)
        
        eye1 = min(eyes,key = lambda eye: eye[0])
        eye2 = max(eyes,key = lambda eye: eye[0])
        ext_ratio = math.dist(eye1,eye2) / self.mask_eyes_dif
        
        rot_degree = 180 - math.atan2(eye1[1]-eye2[1],eye1[0]-eye2[0])*180/math.pi 
        rot_mask = cv2.resize(self.mask,tuple(round(self.mask.shape[1-i]*ext_ratio) for i in range(2)))
        rot_mask = rotate(rot_mask,rot_degree)
        
        #img[:,:] = [0,0,0,255]
        ut.put_sub_image(img,rot_mask,tuple(round(eye1[i] - (self.mask_eyes[1][1-i] * ext_ratio)) for i in range(2)))
        return img


def getBackgroundMask(image):
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)      
    RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = selfie_segmentation.process(RGB)
    return results.segmentation_mask

def removeBackground(image,backgroundImage,backgroundColor=(0,0,0)):
    
    if(backgroundImage is None):
        backgroundImage = np.zeros(image.shape,dtype=np.uint8)
        backgroundImage[:,:] = backgroundColor
    backgroundImage = cv2.resize(backgroundImage,image.shape[:2][::-1])
    
    mask = getBackgroundMask(image)
    condition = np.stack(mask,axis=-1) > 0.5
    condition = np.swapaxes(condition,0,1)
    condition = np.reshape(condition,(condition.shape + (1,)))
    res = condition
    res = np.concatenate((res,condition),axis=-1)
    res = np.concatenate((res,condition),axis=-1)
    #print(res.shape)
    return np.where(res,image,backgroundImage)


if (__name__ == "__main__"):
    an = Anonimaitor2(r"assets\Soviet-era-GettyImages-89856241-1200x720.jpg",r"assets\an1.png")

    cap = cv2.VideoCapture(0)

    while (True):
        rat, frame = cap.read()

        frame = an.anonimaite(frame)
        #frame = cv2.cvtColor(frame,cv2.COLOR_BGRA2BGR)
        print(frame.shape)
        cv2.imshow("img",frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
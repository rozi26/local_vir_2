import cv2
import numpy as np
import mediapipe as mp


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
            self.mask = np.array(cv2.imread(self.mask_path))
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
                eyes[0] += y; eyes[1] += x
                self.eyes = eyes
                break
        if (eyes is None):
            condition = np.stack(mask,axis=-1) > 0.5
            condition = np.swapaxes(condition,0,1)
            condition = np.reshape(condition,(condition.shape + (1,)))
            shadow = np.zeros(img.shape,dtype=np.uint8)
            img = np.where(condition,shadow,self.bg)
        else:
            ps = [(ey[1]+ey[3]//2,ey[0]+ey[2]//2) for ey in eyes]
            cv2.circle(img,ps[0],5,[0,255,0],5)
            cv2.circle(img,ps[1],5,[0,255,0],5)
            print(ps)

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
    an = Anonimaitor(r"assets\Soviet-era-GettyImages-89856241-1200x720.jpg",r"assets\gratis-png-mascara-anonima.png")

    cap = cv2.VideoCapture(0)

    while (True):
        rat, frame = cap.read()

        frame = an.anonimaite(frame)
        cv2.imshow("img",frame)

        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
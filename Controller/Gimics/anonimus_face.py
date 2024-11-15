from imutils import face_utils
import numpy as np
import cv2
import math
from ai_utils import find_faces_dots1
from PIL import Image
from matplotlib import pyplot as plt


FRAME_SHAPE = (480,640)

AI_FUNC = {'func':find_faces_dots1, "eye1":36, "eye2":45, "mouth":(49,61)}

def put_image(img: np.array, sub: np.array, x, y):
    if (x < 0 or y < 0): return put_image(img,sub[max(0,-y):,max(0,-x),:],max(0,x),max(0,y))
    x2, y2 = min(len(img[0]),x+len(sub[0])), min(len(img),y+len(sub))
    sw, sh = x2-x, y2-y
    img[y:y2,x:x2] = sub[:sh,:sw]

class Anonimater():
    def __init__(self, mask, bg):
        self.mask = mask
        self.bg = bg
        self.ai_funcs = AI_FUNC
        
        eyes_loc = np.argwhere(np.all(mask == [255,0,0,255], axis=-1))
        self.mask_eye1 = min(eyes_loc,key=lambda x: x[1])[::-1]
        self.mask_eye2 = max(eyes_loc,key=lambda x: x[1])[::-1]
        self.mask_mount = max(eyes_loc,key=lambda x: x[0])[::-1]

        self.eyes_dits = math.dist(self.mask_eye1,self.mask_eye2)


    def get_image(self, img):
        dots: np.array = AI_FUNC['func'](img)
        if (len(dots) == 0): return img
        eye1, eye2 = dots[self.ai_funcs['eye1']], dots[self.ai_funcs['eye2']]

        mask = np.copy(self.mask)
        
        #draw the mounth
        mounth_points = np.array([p - eye1 + self.mask_eye1 for p in dots[self.ai_funcs['mouth'][0]:self.ai_funcs['mouth'][1]]],dtype=np.int32)
        cv2.fillPoly(mask,[mounth_points],[255,0,0,255])

        size_ratio = math.dist(eye1,eye2) / self.eyes_dits
        mask = cv2.resize(mask,(round(len(self.mask)*size_ratio),round(len(self.mask[0])*size_ratio)))

        res = np.copy(self.bg)        
        put_image(res,mask,eye1[0] - self.mask_eye1[0],eye1[1] - self.mask_eye1[1])
        return res

if (__name__ == "__main__"):

    bg = np.zeros(FRAME_SHAPE + (4,),dtype=np.uint8)
    bg[:,:,3] = 255
    mask = np.array(Image.open(r"F:\programing\python\fun\vir2\Controller\assets\gratis-png-mascara-anonima.png"))
    
    AN = Anonimater(mask,bg)

    cam = cv2.VideoCapture(0)
    while (True):
        ret , frame = cam.read()
        print(frame.shape)
        frame = AN.get_image(frame)
        cv2.imshow("fr",frame)
        if (cv2.waitKey(1) & 0xFF == ord('q')): break
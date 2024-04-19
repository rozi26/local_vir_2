import socket
import numpy as np
import mss
import cv2
import math

def get_ip():
    hostname = socket.gethostname()    
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_screenshot_async(screen=1,pix=None):
     with mss.mss() as sct:
        monitor = sct.monitors[screen]
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        a = 1 if (pix is None) else max(1,math.sqrt(len(img)*len(img[0]/pix)))
        if (a != 1): img = cv2.resize(img,(len(img)//a,len(img[0])//a))
        return np.array(screenshot)
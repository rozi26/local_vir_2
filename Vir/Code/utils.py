import socket
import numpy as np
import mss

def get_ip():
    hostname = socket.gethostname()    
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_screenshot_async(screen=1):
     with mss.mss() as sct:
        monitor = sct.monitors[screen]
        screenshot = sct.grab(monitor)
        return np.array(screenshot)
import socket
import numpy as np
import mss
import cv2
import math
import pyaudio
import wave
import io
import pygame as pg
import ctypes, win32gui, win32ui
from PIL import Image,ImageGrab
import pyautogui as pa

def get_ip():
    hostname = socket.gethostname()    
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def compress_img(img, pix):
    if (pix is None): return img
    a = 1 if (pix is None) else max(1,int(math.sqrt(len(img)*len(img[0])/pix)))
    if (a != 1): img = cv2.resize(img,(len(img[0])//a,len(img)//a))
    return img    

def get_screenshot_async(screen=1,pix=None):
     with mss.mss() as sct:
        monitor = sct.monitors[screen]
        screenshot = sct.grab(monitor)
        img = np.array(screenshot,dtype=np.uint8)
        return compress_img(img,pix)
    
def get_screenshot_async2(screen=1,pix=None):
    def get_cursor():
        hcursor = win32gui.GetCursorInfo()[1]
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 36, 36)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0,0), hcursor)
        
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        cursor = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1).convert("RGBA")
        
        win32gui.DestroyIcon(hcursor)    
        win32gui.DeleteObject(hbmp.GetHandle())
        hdc.DeleteDC()


        pixdata = cursor.load()


        width, height = cursor.size
        for y in range(height):
            for x in range(width):

                if pixdata[x, y] == (0, 0, 0, 255):
                    pixdata[x, y] = (0, 0, 0, 0)


        hotspot = win32gui.GetIconInfo(hcursor)[1:3]

        return (cursor, hotspot)
    cursor, (hotspotx, hotspoty) = get_cursor()
    ratio = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    ratio = 1
    img = ImageGrab.grab(bbox=None, include_layered_windows=True)
    pos_win = pa.position()
    pos = (round(pos_win[0]*ratio - hotspotx), round(pos_win[1]*ratio - hotspoty))
    img.paste(cursor, pos, cursor)
    return compress_img(np.array(img),pix)
    
def have_camera(): 
    cap = cv2.VideoCapture(0)
    return cap.isOpened()

def get_data():
    data = {}
    data['camera'] = have_camera()
    with mss.mss() as sct:
        monitors = sct.monitors
        data['monitors_count'] = len(monitors) - 1
        for i in range(1,len(monitors)): data[f'monitor_{i}'] = monitors[i] 
        
    return data

def record(duration):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = duration
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = b''.join(frames)
    with io.BytesIO() as wav_io:
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(CHANNELS)
                wav_file.setsampwidth(2)
                wav_file.setframerate(RATE)
                wav_file.writeframes(audio_data)

            return wav_io.getvalue()

def play_sound(audio_bytes):
    pg.mixer.init()
    pg.mixer.music.load(audio_bytes)
    pg.mixer.music.play()
    
if (__name__ == "__main__"):
    print(get_data())
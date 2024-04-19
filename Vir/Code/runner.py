import time
import pyautogui as pa
import utils as ut
import io
from gtts import gTTS
import pyaudio
import langid
import tkinter as tk
from threading import Thread

async def prosses_command(data) -> dict:
    command = data["command"]
    if (command == "alive"): return {'message':'alive','time':time.time()}
    if (command == "mouse_move"): pa.moveTo(x=data['x'],y=data['y'])
    if (command == "press"): 
        but,down = data['button'],data['down']
        but = ['','LEFT','MIDDLE','RIGHT'][but]
        print(f"press {but} - {down}")
        if (down): pa.mouseDown(button=but)
        else: pa.mouseUp(button=but)
    if (command == "key_press"):
        add_keys = ['ctrl','shift','win']
        for k in add_keys:
            if ((k in data.keys()) and data[k]): pa.keyDown(k)
        pa.press(chr(data['code']))
        for k in add_keys:
            if (data[k]): pa.keyUp(k)
        
    if (command == "scroll"): pa.scroll(data['amount'])
    if (command == "data"): return ut.get_data()
    if (command == "record_mic"): return {"content":ut.record(data['sec']),'media_type':'audio/wav'}
    if (command == "speak_text"):
        lang = langid.classify(data['text'])[0]
        print(lang)
        if (lang == 'he'): lang = 'hi'
        top = 'co.in' if lang == 'en' else None
        tts = gTTS(text=data['text'],lang=lang,slow=False,tld=top)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        ut.play_sound(audio_bytes)        
    if (command == "show_text"):
        root = tk.Tk()
        root.geometry('400x400')
        root.title(data['title'] if 'title' in data.keys() else 'message')
        label = tk.Label(root,text=data['text'])
        label.pack()
        Thread(target= lambda: root.mainloop()).start()
            
    return {}

if (__name__ == "__main__"):
    import asyncio
    import time
    asyncio.run(prosses_command({'command':'show_text','text':'hello'}))
    time.sleep(5)
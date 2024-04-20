import tkinter as tk
from PIL import Image, ImageTk
import asyncio
import numpy as np
import cv2
import time
from utils import match_ratio_to_bounds, key_to_int
from threading import Thread
from connector import Connector
from pynput.keyboard import Key, Listener


WIDTH = 1200
HEIGHT = 1000
MENU_HEIGHT = 50
MENU_WIDTH = 200
MARGIN = 20

MAX_IMG_WIDTH = WIDTH - MENU_WIDTH - (MARGIN * 2)
MAX_IMG_HEIGHT = HEIGHT - ((MENU_HEIGHT + MARGIN) * 2)

IP = "192.168.1.231"

class ImageUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Viewer")
        self.geometry(f"{WIDTH}x{HEIGHT}")

        #effect vars
        self.connector = Connector(IP)
        self.en_data = self.connector.send_command('data',{})
        self.control_mode = False #does keybord keys and mouse effect the screen
        self.mouse_over = False
        self.ctrl_down = False
        self.shift_down = False

        #pref vars
        self.monitor = 1
        self.pix = 250000
        self.sound_buffer = 0.5
        self.img_shape = (1,1)


        self.top_menu = tk.Frame(self, height=MENU_HEIGHT, bg="lightgray")
        self.top_menu.pack(side="top", fill="x")

        self.bottom_menu = tk.Frame(self, height=MENU_HEIGHT, bg="lightgray")
        self.bottom_menu.pack(side="bottom", fill="x")

        self.right_menu = tk.Frame(self, width=MENU_WIDTH, bg="lightgray")
        self.right_menu.place(x=WIDTH-MENU_WIDTH,y=MENU_HEIGHT,width=MENU_WIDTH,height=HEIGHT-MENU_HEIGHT*2)

        def add_menu_button(text, action):
            button = tk.Button(self.right_menu,text=text,command=action)
            button.pack()
            return button
        self.control_button = add_menu_button("free",self.set_control)

        self.text_box_value = tk.StringVar()
        self.text_box = tk.Entry(self.right_menu, textvariable=self.text_box_value)
        self.text_box.pack()
        add_menu_button('send',lambda: self.connector.send_command('show_text',{'text':str(self.text_box_value.get())}))
        add_menu_button('speak',lambda: self.connector.send_command('speak_text',{'text':str(self.text_box_value.get())}))
        

        self.image_shower = tk.Label(self)
        self.image_shower.place(x=MARGIN,y=MENU_HEIGHT+MARGIN)

        #add the control event listeners
        self.image_shower.bind('<Motion>', lambda e: self.send_control_command('mouse_move',{
            'x':round(self.en_data[f'monitor_{self.monitor}']['width']*e.x/self.img_shape[1]),
            'y':round(self.en_data[f'monitor_{self.monitor}']['height']*e.y/self.img_shape[0])}))
        fs = lambda i,d: self.send_control_command('press',{'button':i,'down':d})
        self.image_shower.bind('<Button-1>', lambda e: fs(1,True))
        self.image_shower.bind('<ButtonRelease-1>', lambda e: fs(1,False))
        self.image_shower.bind('<Button-2>', lambda e: fs(2,True))
        self.image_shower.bind('<ButtonRelease-2>', lambda e: fs(2,False))
        self.image_shower.bind('<Button-3>', lambda e: fs(3,True))
        self.image_shower.bind('<ButtonRelease-3>', lambda e: fs(3,False))
        self.image_shower.bind('<Button-4>', lambda e: self.send_control_command('scroll',{'amount':10}))
        self.image_shower.bind('<Button-5>', lambda e: self.send_control_command('scroll',{'amount':-10}))

        #add keyboard listner
        def add_keyboard_listner():
             with Listener(on_press=self.key_pressed_down_event,on_release=self.key_pressed_up_event) as listener: listener.join()
        self.keyboard_listner_thread = Thread(target=add_keyboard_listner)
        self.keyboard_listner_thread.start()

        # Start updating image
        self.img_updater = Thread(target=self.update_image)
        self.img_updater.start()
    
    def send_control_command(self, command,data):
        print(data)
        if (not self.control_mode): return
        def run():  self.connector.send_command(command,data)
        Thread(target=run).run()
        #self.connector.send_command(command,data)

    def set_control(self):
        self.control_mode = not self.control_mode
        self.control_button.config(text = "control" if self.control_mode else "free")

    def key_pressed_down_event(self,key):
        if (key == Key.shift): self.shift_down = True
        if (key == Key.ctrl_l): self.ctrl_down = True
        try: self.send_control_command('key_press',{'code':key_to_int(key),'shift':self.shift_down,'ctrl':self.ctrl_down})
        except: pass

    def key_pressed_up_event(self,key):
        print("upaAAaA")
        if (key == Key.shift): self.shift_down = False
        if (key == Key.ctrl_l): self.ctrl_down = False

    def update_image(self):
        async def update():
            img = await self.connector.get_screenshot(self.monitor,self.pix)
            #print(match_ratio_to_bounds(len(img[0]),len(img),MAX_IMG_WIDTH,MAX_IMG_HEIGHT))
            img = cv2.resize(img,match_ratio_to_bounds(len(img[0]),len(img),MAX_IMG_WIDTH,MAX_IMG_HEIGHT))
            self.img_shape = img.shape
            pil_image = Image.fromarray(img)
            tk_image = ImageTk.PhotoImage(image=pil_image)
            self.image_shower.configure(image=tk_image,width=len(img[0]),height=len(img))
            self.image_shower.image = tk_image

        while True:
            print("run")
            asyncio.run(update())

if __name__ == "__main__":
    # Create and run the application
    app = ImageUI()
    app.mainloop()
import time
import pyautogui as pa

async def prosses_command(data) -> dict:
    command = data["command"]
    if (command == "alive"): return {'message':'alive','time':time.time()}
    if (command == "move_mouse"): 
        pa.moveTo(x=data['x'],y=data['y'])
    if (command == 'press_key'):
        pass
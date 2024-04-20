import aiohttp
from pynput.keyboard import KeyCode,Key

async def send_post_request_async(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()
        
async def send_get_request_async(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, json=data) as response:
            return await response.read()

def match_ratio_to_bounds(src_width, src_height, max_width, max_height):
    a = min(max_height/src_height,max_width/src_width)
    print(f"a is {a}")
    return (int(src_width*a),int(src_height*a))

def key_to_int(key: KeyCode) -> int:
    if (key == Key.shift): return 14
    if (key == Key.backspace): return 8
    if (key == Key.esc): return 27
    if (key == Key.delete): return 127
    if (key == Key.space): return 32
    if (key == Key.tab): return 9
    if (key == Key.caps_lock): return 20
    if (key == Key.ctrl): return 19
    return ord(key.char)
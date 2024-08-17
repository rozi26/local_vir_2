import aiohttp
import numpy as np
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


def put_sub_image(img: np.array, sub_img: np.array, start_point:tuple):
    print(start_point)
    y_start = max(0, start_point[1])
    y_end = min(len(img), start_point[1] + len(sub_img))
    x_start = max(0, start_point[0])
    x_end = min(len(img[0]), start_point[0] + len(sub_img[0]))
    sub_start_x = x_start-start_point[0]
    sub_start_y = y_start-start_point[1]
    return insert_image(img,sub_img[sub_start_y:(sub_start_y + (y_end-y_start)),sub_start_x:(sub_start_x + (x_end-x_start)),:],x_start,y_start)
    img[y_start:y_end, x_start:x_end,:] = sub_img[sub_start_y:(sub_start_y + (y_end-y_start)),sub_start_x:(sub_start_x + (x_end-x_start)),:]
    return  
    for y in range(y_start,y_end):
        for x in range(x_start, x_end):
            py, px = y - y_start + sub_start_y, x - x_start + sub_start_x
            if (sub_img[py][px][-1] != 255): continue
            img[y][x] = sub_img[py][px]
            
def insert_image(background, overlay, x, y):
    h, w = overlay.shape[:2]

    # Blending based on alpha channel
    alpha_overlay = overlay[:, :, 3] / 255.0
    alpha_background = background[y:y+h, x:x+w, 3] / 255.0

    # Normalize alphas
    combined_alpha = alpha_overlay + alpha_background * (1 - alpha_overlay)
    combined_alpha[combined_alpha == 0] = 1  # To avoid division by zero in normalization

    # Compute weighted sums
    for c in range(3):  # For each color channel
        background[y:y+h, x:x+w, c] = (overlay[:, :, c] * alpha_overlay + 
                                       background[y:y+h, x:x+w, c] * alpha_background * (1 - alpha_overlay)) / combined_alpha

    # Update the alpha channel of the background
    background[y:y+h, x:x+w, 3] = combined_alpha * 255

    return background
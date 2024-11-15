import aiohttp
import socket
import io
import pyaudio
import wave
import asyncio
#import simpleaudio as sa
import time
from pynput.keyboard import KeyCode,Key
from threading import Thread

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

def read_udp(client: socket.socket, buffer_size=2**14, start_size=32):
    client.settimeout(2)
    p1 = client.recv(start_size)
    size = int.from_bytes(p1,"little")
    print(f"size is {size}")
    sd = b""
    while(len(sd) < size):
        print(f"\rgot {len(sd)}   " ,end="")
        chc = client.recv(buffer_size)
        print(len(chc))
        if (not chc or len(chc) != buffer_size): break
        sd += chc
    return sd[:min(len(sd),size)]

def play_sound(data: bytes):
    wave_file = wave.open(io.BytesIO(data),'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wave_file.getsampwidth()),channels=wave_file.getnchannels(),rate=wave_file.getframerate(),output=True)
    chunk_size = 1024
    data_chunk = wave_file.readframes(chunk_size)

    # Play the audio by writing the data to the stream
    while data_chunk:
        stream.write(data_chunk)
        data_chunk = wave_file.readframes(chunk_size)

    # Close and terminate the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

async def get_containes_sound_player(data_getter, step_size: float):
    queue = asyncio.Queue(maxsize=20)
    async def reader():
        while(True):
            if (queue.qsize() == 0): await asyncio.sleep(step_size/10)
            else:
                data = await queue.get()
                print(f"read data from size {queue.qsize()}")
                #pobj = sa.play_buffer(data,1,2,44100)
                #pobj.wait_done()

    async def loader():
        async def load():
            print("load part")
            await queue.put(await data_getter(step_size))
        while (True):
            t1 = time.perf_counter()
            asyncio.create_task(load())
            t2 = time.perf_counter()
            await asyncio.sleep(step_size*0.8)
            print(f"time take {t2-t1} and {time.perf_counter()-t2}")

    asyncio.create_task(reader())
    await loader()

def int_to_bytes(num: int, size: int = 4) -> bytes:
    return num.to_bytes(size, byteorder='little')
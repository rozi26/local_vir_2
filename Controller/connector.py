import requests
import aiohttp
import numpy as np
import time
import io
import asyncio
from utils import send_get_request_async, send_post_request_async
from PIL import Image
from matplotlib import pyplot as plt

class Connector:
    def __init__(self,ip,port=8000) -> None:
        self.url = f"http://{ip}:{port}"
    
    async def send_command_async(self,command,data:dict={}) -> dict:
        data["command"] = command
        return await send_post_request_async(f"{self.url}/command",data)
    
    def send_command(self,command,data:dict={}) -> dict:
        data["command"] = command
        return requests.post(f"{self.url}/command",json=data).json()
    
    async def get_screenshot(self,monitor=1,pix=150000) -> np.array:
        data = {"monitor":monitor,"pix":pix}
        img_data = await send_get_request_async(f"{self.url}/screenshot",data)
        print(f"data len is {len(img_data)}")
        img = np.array(Image.open(io.BytesIO(img_data)))
        return img
    

async def test():
    con = Connector("192.168.1.231")
    img = await con.get_screenshot()

if (__name__ == "__main__"):
    asyncio.run(test())
    time.sleep(10)

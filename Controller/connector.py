import requests
import aiohttp
import numpy as np
import time
import io
import asyncio
import socket
import struct
import pickle
import PIL
import cv2
import utils as ut
import json
from utils import send_get_request_async, send_post_request_async, read_udp
from PIL import Image
from matplotlib import pyplot as plt

class Connector:
    def __init__(self,ip,port=8000) -> None:
        self.ip = ip
        self.url = f"{ip}:{port}"

        self.stream_socket = None
        self.stream_payload_size = None
        self.config = None
    
    async def get_config(self):
        if (self.config is None): self.config = await self.send_command_async("set_config")
        return self.config
    
    async def update_config(self):
        await self.send_command_async('set_config',{'config':self.config})

    async def send_command_async(self,command,data:dict=None) -> dict:
        if (data is None): data = {}
        data["command"] = command
        return await send_post_request_async(f"{self.url}/command",data)
    
    def send_command(self,command,data:dict={}) -> dict:
        data["command"] = command
        return requests.post(f"{self.url}/command",json=data,timeout=5).json()
    
    async def get_screenshot(self,monitor=1,pix=150000) -> np.array:
        try:
            data = {"monitor":monitor,"pix":pix}
            img_data = await send_get_request_async(f"{self.url}/screenshot",data)
            print(f"data len is {len(img_data)}")
            img = np.array(Image.open(io.BytesIO(img_data)))
            return img
        except:
            return None
        
    async def get_screenshot2(self, port=1024, pix=150000) -> np.array:
        config = await self.get_config()
        if (config['ImagePixels'] != pix):
            config['ImagePixels'] = pix
            await self.update_config()

        if (self.stream_socket is None):
            self.stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stream_socket.connect((self.ip,port))
            self.stream_payload_size = struct.calcsize('Q')
            pass

        while (True):
            len_message = self.stream_socket.recv(4)
            data_len = sum([len_message[i]<<(i*8) for i in range(4)])
            
            data = b""
            while (len(data) < data_len):
                data += self.stream_socket.recv(data_len - len(data))
            frame = np.array(Image.open(io.BytesIO(data)))
            if (__name__ == "__main__"):
                cv2.imshow("vid",frame)
                if ((cv2.waitKey(1) & 0xFF) == ord('q')): break
            else: break
        return frame

        
    async def get_record(self, time: float):
        res = await send_get_request_async(f"{self.url}/record",{'time':time})
        return res
    

class Connector2:
    def __init__(self, ip, port=8000):
        self.ip = ip
        self.port = port
        self.stream_socket = None
        self.stream_payload_size = None
        self.config = None

    async def get_config(self):
        if self.config is None:
            self.config = await self.send_command("set_config")
        return self.config

    async def update_config(self):
        await self.send_command('set_config', {'config': self.config})

    async def send_command(self, command, data=None):
        if data is None:
            data = {}
        data["command"] = command
        response = await self._send_socket_request(data)
        return response

    async def get_screenshot(self, monitor=1, pix=150000) -> np.array:
        try:
            data = {"command": "screenshot", "monitor": monitor, "pix": pix}
            img_data = await self._send_socket_request(data, expect_binary=True)
            img = np.array(Image.open(io.BytesIO(img_data)))
            return img
        except Exception as e:
            print(f"Error getting screenshot: {e}")
            return None

    async def _send_socket_request(self, data, expect_binary=False):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.ip, self.port))

            # Convert the dictionary to JSON, then to bytes with UTF-8 encoding
            json_data = json.dumps(data).encode('utf-8')
            
            # Send the length of the JSON data as a 4-byte header, then the JSON data itself
            data_length = ut.int_to_bytes(len(json_data))
            sock.sendall(data_length + json_data)
            print(f"data len: {len(json_data)}")

            # Receive the response length header
            response_length_header = sock.recv(4)
            response_length = struct.unpack('>I', response_length_header)[0]

            # Receive the actual response data
            response_data = b""
            while len(response_data) < response_length:
                packet = sock.recv(response_length - len(response_data))
                if not packet:
                    break
                response_data += packet

            # If expecting binary (for image), return raw binary data, else decode the JSON response
            if expect_binary:
                return response_data
            else:
                response_text = response_data.decode('utf-8')
                response = json.loads(response_text)
                return response

    async def get_record(self, time: float):
        data = {"command": "record", "time": time}
        res = await self._send_socket_request(data)
        return res


async def test():

    con = Connector2("10.100.102.6")
    res = await con.get_config()
    print(f"resive {res}")

if (__name__ == "__main__"):
    asyncio.run(test())
    time.sleep(10)

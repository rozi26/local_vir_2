import requests
import aiohttp

async def send_post_request_async(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

class Connector:
    def __init__(self,ip,port=8000) -> None:
        self.url = f"http://{ip}:{port}"
    
    async def send_command_async(self,command,data:dict) -> dict:
        data["command"] = command
        return await send_post_request_async(self.url,data)
    

if (__name__ == "__main__"):
    pass
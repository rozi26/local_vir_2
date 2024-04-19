import aiohttp

async def send_post_request_async(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()
        
async def send_get_request_async(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, json=data) as response:
            return await response.read()
        
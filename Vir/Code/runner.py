import time

async def prosses_command(data) -> dict:
    command = data["command"]
    if (command == "alive"): return {'message':'alive','time':time.time()}

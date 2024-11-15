import datetime
import socket
import json
from flask import Flask, request, jsonify
from waitress import serve
from flask_cors import CORS
from threading import Thread

LOG_PATH = r"F:\programing\python\fun\vir2\Controller\logs.txt"
REMOTE_LOGGER_PORT = 1025

def write_log_message(message: str):
    with open(LOG_PATH,'r') as f:
        txt = f.read()
        f.close()
    
    txt = f"{datetime.datetime.now()}: \t-> {message}\n" + txt
    with open(LOG_PATH, 'w') as f:
        f.write(txt)
        f.close()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.post("/")
def report_log():
    data = json.loads(request.get_json())
    user_ip = request.remote_addr
    try:
        write_log_message(f'from {user_ip} got [{data["message"]}]')
    except Exception as e:
        write_log_message(f"crash from {user_ip}")
    return jsonify({})

def open_resiver():
    IP = socket.gethostbyname(socket.gethostname()) 
    def p_open_resiver(): serve(app,host=IP, port=REMOTE_LOGGER_PORT)
    Thread(target=p_open_resiver).start()
    write_log_message(f"open resiver at {IP}:{REMOTE_LOGGER_PORT}")

if (__name__ == "__main__"):
    open_resiver()
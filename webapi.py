#!/usr/bin/python


import json
import socket
import threading

from sanic import Sanic
from sanic.response import json as json_response


pos_lock = threading.Lock()
positions = [[0, 0], [0, 0], [0, 0], [0, 0]]

app = Sanic()


@app.route("/positions")
async def get_positions(request):
    with pos_lock:
        _positions = positions[:]
    return json_response([{"x": p[0], "y": p[1]} for p in _positions])


def ipc_thread():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/tmp/xwiimote-server.sock')
    with sock.makefile() as f:
        for line in f:
            msg = json.loads(line)
            with pos_lock:
                positions[:] = msg

def webapi_thread():
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    ipc_thr = threading.Thread(target=ipc_thread, daemon=True)
    ipc_thr.start()
    webapi_thread()

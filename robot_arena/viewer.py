#!/usr/bin/python


import json
import socket
import threading

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


pos_lock = threading.Lock()
positions = [[0, 0], [0, 0], [0, 0], [0, 0]]


def display_thread():
    """Display IR positions in a matplotlib window.

    Needs to be run as the main thread, because the Qt backend of matplotlib
    cannot handle running in any other thread.
    """

    fig, ax = plt.subplots()
    ax.set_xlim(0, 1024)
    ax.set_ylim(0, 1024)
    ax.set_xticks(range(0, 1025, 256))
    ax.set_yticks(range(0, 1025, 256))
    ax.grid(linestyle='--')
    with pos_lock:
        scatter = ax.scatter([p[0] for p in positions], [p[1] for p in positions], c='brgy')

    def update(frame):
        with pos_lock:
            _positions = positions[:]
        scatter.set_offsets(_positions)

    animation = FuncAnimation(fig, update, interval=100)
    plt.show()


def ipc_thread():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/tmp/xwiimote-server.sock')
    with sock.makefile() as f:
        for line in f:
            msg = json.loads(line)
            with pos_lock:
                positions[:] = msg


if __name__ == '__main__':
    ipc_thr = threading.Thread(target=ipc_thread, daemon=True)
    ipc_thr.start()
    display_thread()

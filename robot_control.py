#!/usr/bin/python


import json
import os
import os.path
import select
import socket
import threading

import xwiimote


def xwiimote_paths():
    """Return a list of connected Wiimote devices."""
    paths = []
    mon = xwiimote.monitor(False, False)
    path = mon.poll()
    while path is not None:
        paths.append(path)
        path = mon.poll()
    return paths


def wiimote_thread():
    """Continuously wait for Wiimote events and process them."""
    p = xwiimote_paths()[0]
    ev = xwiimote.event()
    iface = xwiimote.iface(p)
    iface.open(xwiimote.IFACE_IR)
    with socket.socket(socket.AF_UNIX, type=socket.SOCK_STREAM) as sock:
        if os.path.exists('/tmp/xwiimote-server.sock'):
            os.remove('/tmp/xwiimote-server.sock')
        sock.bind('/tmp/xwiimote-server.sock')
        sock.listen()

        ep = select.epoll()
        ep.register(sock.fileno(), select.EPOLLIN)
        ep.register(iface.get_fd(), select.EPOLLIN)

        clients = set()

        while True:
            events = ep.poll()

            for fileno, event in events:
                if fileno == sock.fileno():
                    clients.add(sock.accept()[0])

                elif fileno == iface.get_fd():
                    iface.dispatch(ev)
                    if ev.type == xwiimote.EVENT_IR:
                        abs_ = [ev.get_abs(n)[:2] for n in range(4)]
                        positions = (json.dumps(abs_) + '\n').encode('ascii')
                        dead_clients = set()
                        for client in clients:
                            try:
                                client.send(positions)
                            except:
                                dead_clients.add(client)
                        clients -= dead_clients
                        for client in dead_clients:
                            client.close()
                    else:
                        print('event: {}'.format(ev.type))

    iface.close(xwiimote.IFACE_IR)


if __name__ == '__main__':
    wiimote_thread()

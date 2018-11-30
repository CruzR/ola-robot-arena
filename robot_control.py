#!/usr/bin/python


import queue
import select
import threading

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
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


pos_lock = threading.Lock()
xvals = [0, 0, 0, 0]
yvals = [0, 0, 0, 0]

accel_lock = threading.Lock()
accel = [0.0, 0.0, 0.0]


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
    scatter = ax.scatter(xvals, yvals, c='brgy')

    def update(frame):
        with pos_lock:
            _xvals = xvals[:]
            _yvals = yvals[:]
        with accel_lock:
            _accel = accel[:]
        scatter.set_offsets([[_xvals[i], _yvals[i]] for i in range(4)])

    animation = FuncAnimation(fig, update, interval=100)
    plt.show()


def wiimote_thread():
    """Continuously wait for Wiimote events and process them."""
    p = xwiimote_paths()[0]
    ev = xwiimote.event()
    iface = xwiimote.iface(p)
    iface.open(xwiimote.IFACE_ACCEL|xwiimote.IFACE_IR)
    fd = iface.get_fd()
    ep = select.epoll.fromfd(fd)
    while True:
        events = dict(ep.poll())
        iface.dispatch(ev)
        if ev.type == xwiimote.EVENT_ACCEL:
            _accel = ev.get_abs(0)
            with accel_lock:
                accel[:] = _accel
        elif ev.type == xwiimote.EVENT_IR:
            abs_ = [ev.get_abs(n) for n in range(4)]
            _xvals = [v[0] for v in abs_]
            _yvals = [v[1] for v in abs_]
            with pos_lock:
                xvals[:] = _xvals
                yvals[:] = _yvals
        else:
            print('event: {}'.format(ev.type))
    iface.close(xwiimote.IFACE_ACCEL|xwiimote.IFACE_IR)


if __name__ == '__main__':
    wiimote_thr = threading.Thread(target=wiimote_thread, daemon=True)
    wiimote_thr.start()
    display_thread()

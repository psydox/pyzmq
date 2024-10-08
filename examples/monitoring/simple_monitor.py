"""Simple example demonstrating the use of the socket monitoring feature."""

# This file is part of pyzmq.
#
# Distributed under the terms of the New BSD License. The full
# license is in the file LICENSE.BSD, distributed as part of this
# software.

__author__ = 'Guido Goldstein'

import threading
import time
from typing import Any, Dict

import zmq
from zmq.utils.monitor import recv_monitor_message


def line() -> None:
    print('-' * 40)


print(f"libzmq-{zmq.zmq_version()}")
if zmq.zmq_version_info() < (4, 0):
    raise RuntimeError("monitoring in libzmq version < 4.0 is not supported")

EVENT_MAP = {}
print("Event names:")
for name in dir(zmq):
    if name.startswith('EVENT_'):
        value = getattr(zmq, name)
        print(f"{name:21} : {value:4}")
        EVENT_MAP[value] = name


def event_monitor(monitor: zmq.Socket) -> None:
    while monitor.poll():
        evt: Dict[str, Any] = {}
        mon_evt = recv_monitor_message(monitor)
        evt.update(mon_evt)
        evt['description'] = EVENT_MAP[evt['event']]
        print(f"Event: {evt}")
        if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
            break
    monitor.close()
    print()
    print("event monitor thread done!")


ctx = zmq.Context.instance()
rep = ctx.socket(zmq.REP)
req = ctx.socket(zmq.REQ)

monitor = req.get_monitor_socket()

t = threading.Thread(target=event_monitor, args=(monitor,))
t.start()

line()
print("bind req")
req.bind("tcp://127.0.0.1:6666")
req.bind("tcp://127.0.0.1:6667")
time.sleep(1)

line()
print("connect rep")
rep.connect("tcp://127.0.0.1:6667")
time.sleep(0.2)
rep.connect("tcp://127.0.0.1:6666")
time.sleep(1)

line()
print("disconnect rep")
rep.disconnect("tcp://127.0.0.1:6667")
time.sleep(1)
rep.disconnect("tcp://127.0.0.1:6666")
time.sleep(1)

line()
print("close rep")
rep.close()
time.sleep(1)

line()
print("disabling event monitor")
req.disable_monitor()

line()
print("event monitor thread should now terminate")

# Create a new socket to connect to listener, no more
# events should be observed.
rep = ctx.socket(zmq.REP)

line()
print("connect rep")
rep.connect("tcp://127.0.0.1:6667")
time.sleep(0.2)

line()
print("disconnect rep")
rep.disconnect("tcp://127.0.0.1:6667")
time.sleep(0.2)

line()
print("close rep")
rep.close()

line()
print("close req")
req.close()

print("END")
ctx.term()

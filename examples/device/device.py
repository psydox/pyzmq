"""Demonstrate using zmq.proxy device for message relay"""

# This example is placed in the Public Domain
# It may also be used under the Creative Commons CC-0 License, (C) PyZMQ Developers

import time
from threading import Thread

import zmq

MSGS = 10
PRODUCERS = 2


def produce(url, ident):
    """Produce messages"""
    ctx = zmq.Context.instance()
    s = ctx.socket(zmq.PUSH)
    s.connect(url)
    print(f"Producing {ident}")
    for i in range(MSGS):
        s.send((f'{ident}: {time.time():.0f}').encode())
        time.sleep(1)
    print(f"Producer {ident} done")
    s.close()


def consume(url):
    """Consume messages"""
    ctx = zmq.Context.instance()
    s = ctx.socket(zmq.PULL)
    s.connect(url)
    print("Consuming")
    for i in range(MSGS * PRODUCERS):
        msg = s.recv()
        print(msg.decode('ascii'))
    print("Consumer done")
    s.close()


def proxy(in_url, out_url):
    ctx = zmq.Context.instance()
    in_s = ctx.socket(zmq.PULL)
    in_s.bind(in_url)
    out_s = ctx.socket(zmq.PUSH)
    out_s.bind(out_url)
    try:
        zmq.proxy(in_s, out_s)
    except zmq.ContextTerminated:
        print("proxy terminated")
        in_s.close()
        out_s.close()


in_url = 'tcp://127.0.0.1:5555'
out_url = 'tcp://127.0.0.1:5556'

consumer = Thread(target=consume, args=(out_url,))
proxy_thread = Thread(target=proxy, args=(in_url, out_url))
producers = [Thread(target=produce, args=(in_url, i)) for i in range(PRODUCERS)]

consumer.start()
proxy_thread.start()

for p in producers:
    p.start()

consumer.join()
zmq.Context.instance().term()

from asyncio import Future,run,get_event_loop,get_running_loop,sleep
from aiosix.posix import aio_read_kevent
from os import open, O_RDONLY, O_NONBLOCK
from select import (
    kqueue, kevent,
    KQ_FILTER_VNODE,
    KQ_NOTE_WRITE,
    KQ_EV_ADD,
    KQ_EV_ONESHOT,
)
from selectors import KqueueSelector, EVENT_READ

kq = kqueue()
kqfd = kq.fileno()

def receive_result():
    print('receive_result')
    results = kq.control(None, 1, 0)
    print(results)

def do_io(fd, buf):
    fut = Future()
    aio_read_kevent(kqfd, fd, buf, 0, fut)
    return fut

async def main():
    loop = get_running_loop()
    loop.add_reader(kq.fileno(), receive_result)
    fd = open("file", O_RDONLY)
    buf = bytearray(16)
    do_io(fd, buf)
    await sleep(20)

run(main())

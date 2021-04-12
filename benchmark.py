from aiosix._aio import ffi,lib
from asyncio import get_event_loop,gather
from asyncio.unix_events import _UnixSelectorEventLoop
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from random import randrange,randbytes
from timeit import timeit
from os import (
    open, close, pread, pwrite,
    O_RDONLY, O_WRONLY, O_CREAT, O_EXCL,
)
from pathlib import Path
from select import (
    KQ_EV_ONESHOT,
    KQ_FILTER_AIO,
    KQ_FILTER_READ,
    KQ_FILTER_WRITE,
)
from selectors import (
    KqueueSelector,
    EVENT_READ,
    EVENT_WRITE,
)
from sys import argv

KiB = 1024
MiB = 1024 * KiB

NUM_OPS = 64 * 1024
NUM_WORKERS = 128
NUM_THREADS = 8

FILE_SIZE = 4 * MiB
BUF_SIZE = 4 * KiB

class AioKqueueSelector(KqueueSelector):
    def __init__(self):
        super().__init__()
        self.iocb_map = {}

    def select(self, timeout=None):
        timeout = None if timeout is None else max(timeout, 0)
        max_ev = max(len(self._fd_to_key), 1)
        ready = []
        try:
            kev_list = self._selector.control(None, max_ev, timeout)
        except InterruptedError:
            return ready
        for kev in kev_list:
            if kev.filter == KQ_FILTER_AIO:
                fut,cbuf,iocb = self.iocb_map.pop(kev.ident)
                if (n := lib.aio_return(iocb)) == -1:
                    fut.set_exception(OSError(ffi.errno))
                else:
                    fut.set_result(bytes(ffi.buffer(cbuf, n)))
                continue
            fd = kev.ident
            flag = kev.filter
            events = 0
            if flag == KQ_FILTER_READ:
                events |= EVENT_READ
            if flag == KQ_FILTER_WRITE:
                events |= EVENT_WRITE

            key = self._key_from_fd(fd)
            if key:
                ready.append((key, events & key.events))
        return ready

class looped:
    def __init__(self):
        self.selector = AioKqueueSelector()
        self.loop = _UnixSelectorEventLoop(self.selector)
        self.kqfd = self.selector._selector.fileno()

    def do_io(self, fd, size, offset):
        cbuf = ffi.new("char[]", size)
        iocb = ffi.new("struct aiocb*")
        iocb.aio_fildes = fd
        iocb.aio_offset = offset
        iocb.aio_buf = cbuf
        iocb.aio_nbytes = size
        lib.aiocb_kqueue(iocb, self.kqfd, KQ_EV_ONESHOT, 0)
        lib.aio_read(iocb)

        fut = self.loop.create_future()
        ident = int(ffi.cast("uintptr_t", iocb))
        self.selector.iocb_map[ident] = (fut, cbuf, iocb)
        return fut

# man read: The system guarantees to read the number of bytes requested
# if the descriptor references a normal file that has that many bytes
# left before the end-of-file [...]
class threaded:
    def __init__(self):
        self.loop = get_event_loop()
        self.executor = ThreadPoolExecutor(NUM_THREADS)

    def do_io(self, fd, size, offset):
        return self.loop.run_in_executor(
            self.executor, pread, fd, size, offset
        )

_offsets = deque()

async def worker_task(loop, fd, impl):
    while _offsets:
        assert(
            len(await impl(fd, BUF_SIZE, _offsets.pop())) == BUF_SIZE
        )

def main(impl, number=10):
    for _ in range(NUM_OPS):
        _offsets.append(randrange(0, FILE_SIZE - BUF_SIZE))

    impl = impl()
    loop = impl.loop
    base = Path(argv[1])
    files = []
    tasks = []

    try:
        for i in range(NUM_WORKERS):
            fi = base / f"file.{i:03}"
            fd = open(fi, O_WRONLY | O_CREAT | O_EXCL)
            pwrite(fd, randbytes(FILE_SIZE), 0)
            close(fd)
            fd = open(fi, O_RDONLY)
            files.append((fi,fd))
            tasks.append(loop.create_task(worker_task(loop, fd, impl.do_io)))

        print(
            timeit(
                lambda: loop.run_until_complete(gather(*tasks)),
                number=1
            )
        )

    finally:
        for fi,fd in files:
            close(fd)
            fi.unlink()

if __name__ == '__main__':
    print('THREADED')
    main(threaded)
    main(threaded)
    main(threaded)
    print('LOOPED')
    main(looped)
    main(looped)
    main(looped)

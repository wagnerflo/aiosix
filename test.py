from aiosix.posix import aio_read_kevent
from os import open, O_RDONLY, O_NONBLOCK
from select import kqueue

kq = kqueue()
fd = open(__file__, O_RDONLY | O_NONBLOCK)
buf = bytearray(16)

x = aio_read_kevent(kq.fileno(), fd, buf, 0)
print(x)
print(kq.control(None, 1))

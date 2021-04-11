from aiosix._aio import ffi,lib
from select import kqueue,KQ_EV_ONESHOT,KQ_FILTER_AIO,KQ_EV_EOF
from os import open,O_RDONLY,pread,strerror

kq = kqueue()
fildes = open(__file__, O_RDONLY)
buf = bytearray(1024)

# Set up C handles to our buffer and an iocb struct.
#
# IMPORTANT: Make sure these two don't go out of scope and are garbage
# collected/freed until the aio request has been collected with a call
# to aio_return(iocb).
cbuf = ffi.from_buffer(buf, require_writable=True)
iocb = ffi.new("struct aiocb*")
iocb.aio_fildes = fildes
iocb.aio_offset = 0
iocb.aio_buf = cbuf
iocb.aio_nbytes = len(cbuf)

# Call our small helper from cffi/aiocb_kqueue.c to set up kqueue
# notification for this aio request.
#
# Without KQ_EV_ONESHOT, calls to kqueue.control() keep will keep
# returning the same kevent for the aio_read() until aio_return(iocb)
# has been called.
lib.aiocb_kqueue(iocb, kq.fileno(), KQ_EV_ONESHOT, 0)

# Enqueue the request then wait for it to complete.
lib.aio_read(iocb)
kev = kq.control(None, 10).pop()

assert(kev.filter == KQ_FILTER_AIO)
assert(kev.flags  == KQ_EV_EOF | KQ_EV_ONESHOT)

# According to https://bit.ly/327YlyZ you wouldn't actually need to do
# this. No concrete explanation is given but there are probably simply
# no error conditions that can happen after kqueue has already sent an
# event.
assert(lib.aio_error(iocb) == 0)

# Get the return value of the request. This is equivalent to what the
# synchronous read(2), write(2) and so on would return.
if (n := lib.aio_return(iocb)) == -1:
    raise OSError(ffi.errno, strerror(ffi.errno))

# Accoring to https://bit.ly/3dZmNrY the "original object is kept alive
# (and, in case of memoryview, locked) as long as the cdata object
# returned by ffi.from_buffer() is alive."
ffi.release(cbuf)

assert(buf[:n] == pread(fildes, 1024, 0))

# aiosix

> :warning: This is repository is just a placeholder and some notes for
> a future implementation and an attempt to reserve the project name.

## Notes
- POSIX AIO functions on Linux are [implemented in glibc
  and use threads](https://man7.org/linux/man-pages/man7/aio.7.html#NOTES).
- FreeBSD implementation on the other hand is in [kernel
  space](https://www.freebsd.org/cgi/man.cgi?query=aio)
- Obviously same API though.
- FreeBSD asyncio implementation makes most sense together with kqueue.
  Check if this is used in the current event loop implementation with
  ```python
  isinstance(getattr(loop, "_selector"), selectors.KqueueSelector)
  ```
- Don't forget to make the open call itself non-blocking with
  ```python
  os.open(path, os.O_NONBLOCK | ...)
  ```

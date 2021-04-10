# aiosix

> :warning: This is repository is just a placeholder and some notes for
> a future implementation and an attempt to reserve the project name.

## Notes
- POSIX AIO functions on Linux are [implemented in glibc
  and use threads](https://man7.org/linux/man-pages/man7/aio.7.html#NOTES).
- FreeBSD implementation on the other hand is in [kernel
  space](https://www.freebsd.org/cgi/man.cgi?query=aio)
- Obviously same API though.
- FreeBSD asyncio implementation use makes most sense together with kqueue,
  but the asyncio SelectorEventLoop uses the selectors module which
  only supports readable/writeable notifications that make no sense on
  files. This calls for a custom FreeBSDKeventLoop.
- Don't forget to make the open/close calls non-blocking by running
  them in an executor.
- Python example how to use [select.kqueue for arbitrary
  kevents](https://stackoverflow.com/a/63919879).
- Example for [signalfd based
  notifications](https://gist.github.com/mopemope/5413768).
- Stackoverflow answer how to do [realtime signals
  right](https://stackoverflow.com/a/35121643).
- NGINX has an [aio
  implementation](https://github.com/firebase/nginx/blob/master/src/os/unix/ngx_file_aio_read.c)
  that can be a reference.

## Operating system support
|         | Backend                         | Notifications    |
| ------- | ------------------------------- | ---------------- |
| FreeBSD | kernel processes                | kqueue           |
| NetBSD  | "largely resides in the kernel" | realtime signals |
| Linux   | userspace threads               | signalfd         |

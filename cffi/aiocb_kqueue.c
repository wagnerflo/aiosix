#include <aio.h>

void aiocb_kqueue(struct aiocb* iocb,
                  int fildes,
                  unsigned short kevent_flags,
                  int sival_int) {
  iocb->aio_sigevent.sigev_notify = SIGEV_KEVENT;
  iocb->aio_sigevent.sigev_notify_kqueue = fildes;
  iocb->aio_sigevent.sigev_notify_kevent_flags = kevent_flags;
  iocb->aio_sigevent.sigev_value.sival_int = sival_int;
}

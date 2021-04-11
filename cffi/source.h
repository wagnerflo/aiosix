#include <aio.h>

void aiocb_kqueue(
  struct aiocb* iocb,
  int fildes,
  unsigned short kevent_flags
);

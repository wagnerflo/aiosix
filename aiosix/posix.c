#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <aio.h>
#include <signal.h>
#include <sys/event.h>

#define CAPSULE_AIOCB "struct aiocb"

static inline int require_nargs(const char* name, Py_ssize_t nargs, Py_ssize_t expected) {
  if (nargs != expected) {
    PyErr_Format(
      PyExc_TypeError,
      "%s() expected %i arguments but got %i instead",
      name, expected, nargs
    );
  }
  return nargs != expected;
}

static PyObject* aio_read_kevent(PyObject* m, PyObject* const* args, Py_ssize_t nargs) {
  if (require_nargs("aio_read_kevent", nargs, 5)) {
    return NULL;
  }

  PyObject* kqueue_fd = args[0];
  PyObject* file_fd = args[1];
  PyObject* bytearray = args[2];
  PyObject* offset = args[3];

  if (!PyByteArray_CheckExact(bytearray)) {
    PyErr_SetString(
      PyExc_TypeError,
      "aio_read_kevent() expected bytearray as third arguments"
    );
    return NULL;
  }

  struct aiocb* iocb = (struct aiocb*) calloc(1, sizeof(struct aiocb));
  if (!iocb)
    return PyErr_NoMemory();

  iocb->aio_fildes = PyLong_AsUnsignedLong(file_fd);
  iocb->aio_offset = PyLong_AsUnsignedLong(offset);
  iocb->aio_buf = PyByteArray_AsString(bytearray);
  iocb->aio_nbytes = PyByteArray_Size(bytearray);

  iocb->aio_sigevent.sigev_notify = SIGEV_KEVENT;
  iocb->aio_sigevent.sigev_notify_kqueue = PyLong_AsUnsignedLong(kqueue_fd);
  iocb->aio_sigevent.sigev_notify_kevent_flags = EV_ONESHOT;
  // !!!! BAD IDEA ????
  // event might get lost (according to people on the internet) and thus
  // object lost, too
  iocb->aio_sigevent.sigev_value.sigval_ptr = args[4];

  if (aio_read(iocb)) {
    PyErr_SetFromErrno(PyExc_OSError);
    return NULL;
  }

  Py_RETURN_NONE;
}

// PyCapsule_IsValid

static PyMethodDef methods[] = {
  { "aio_read_kevent", (PyCFunction) aio_read_kevent, METH_FASTCALL, NULL },
  { NULL, NULL, 0, NULL }
};

static struct PyModuleDef module = {
  PyModuleDef_HEAD_INIT,
  "aiosix.posix",
  NULL,
  -1,
  methods
};

PyMODINIT_FUNC PyInit_posix(void) {
  return PyModule_Create(&module);
}

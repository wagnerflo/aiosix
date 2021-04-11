from cffi import FFI
from pathlib import Path

curdir = Path(__file__).parent
ffibuilder = FFI()
ffibuilder.set_source(
    "aiosix._aio",
    (curdir / "source.h").read_text(),
    sources=[
        str(curdir / filename) for filename in [
            "aiocb_kqueue.c",
        ]
    ]
)
ffibuilder.cdef(
    (curdir / "cdef").read_text()
)

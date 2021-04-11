from pathlib import Path
from setuptools import setup,Extension

setup(
    name="aiosix",
    description=" Python bindings for POSIX aio functions.",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    version="0.1",
    author="Florian Wagner",
    author_email="florian@wagner-flo.net",
    url="https://github.com/wagnerflo/aiosix",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: C",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
    ],
    license_files=["LICENSE"],
    python_requires=">=3.8",
    setup_requires=[
        "cffi>=1.0.0",
    ],
    install_requires=[
        "cffi>=1.0.0",
    ],
    cffi_modules=[
        "cffi/build.py:ffibuilder",
    ],
    packages=[
        "aiosix",
    ],
)

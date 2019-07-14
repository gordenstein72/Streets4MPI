from distutils.core import setup

setup(
    version='0.1dev',
    packages=['project', ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
)

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        "hello",
        ["hello.pyx"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
    )
]

setup(
    name='StreetsParallelized',
    version='0.1dev',
    ext_modules=cythonize(ext_modules),
)
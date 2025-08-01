from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy, pathlib

here = pathlib.Path(__file__).parent

ext_modules = cythonize(
    Extension(
        "spec2gb.pyboy_bridge",
        sources=["spec2gb/pyboy_bridge.pyx"],
        include_dirs=[numpy.get_include()],
    ),
    compiler_directives={"language_level": "3"},
)

setup(name="spec2gb", version="0.0.1", packages=["spec2gb"], ext_modules=ext_modules)

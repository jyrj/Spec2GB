# cython: language_level=3
cimport cython
import numpy as np                    # keeps the NumPy header visible

from pyboy.pyboy cimport PyBoy        # <-- correct qualified name
from pyboy.core.mb cimport Motherboard
from pyboy.core.cpu cimport CPU

cpdef Motherboard get_mb(PyBoy obj):
    """Return the hidden Motherboard instance."""
    return obj.mb

cpdef CPU get_cpu(PyBoy obj):
    """Return the embedded CPU instance."""
    return obj.mb.cpu

cpdef tick_cpu(PyBoy obj, long cycles=1):
    """Tick the LR35902 core `cycles` times (with the GIL held)."""
    return obj.mb.cpu.tick(cycles)

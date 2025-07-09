# tests/test_cpu_vs_pyboy.py
import tempfile, inspect, pytest, sys
from pyboy import PyBoy
from generated.cpu import CPU  # adjust if your CPU lives elsewhere

# ─────────────────────────  3-byte program  ─────────────────────────
# LD A,5  (0x3E 0x05)  ;  ADD A,A  (0x87)
PROG = bytes([0x3E, 0x05, 0x87])

# ───────────────  Build a valid 32 KB ROM image (header + padding) ───────────────
header = bytearray(0x150)

# Put code at reset vector 0x0100
header[0x100 : 0x100 + len(PROG)] = PROG

# Official Nintendo logo (48 bytes, mandatory)
header[0x104 : 0x134] = bytes([
    0xCE,0xED,0x66,0x66,0xCC,0x0D,0x00,0x0B,0x03,0x73,0x00,0x83,
    0x00,0x0C,0x00,0x0D,0x00,0x08,0x11,0x1F,0x88,0x89,0x00,0x0E,
    0xDC,0xCC,0x6E,0xE6,0xDD,0xDD,0xD9,0x99,0xBB,0xBB,0x67,0x63,
    0x6E,0x0E,0xEC,0xCC,0xDD,0xDC,0x99,0x9F,0xBB,0xB9,0x33,0x3E
])

header[0x134:0x13B] = b"ADDTEST"  # simple title
header[0x147] = 0x00              # cartridge type 0  (ROM only)
header[0x148] = 0x00              # ROM size 0  (32 KB)

# header checksum (GB spec)
cs = 0
for b in header[0x134:0x14D]:
    cs = (cs - b - 1) & 0xFF
header[0x14D] = cs

ROM_BYTES = bytes(header) + bytes(0x8000 - len(header))  # pad to 32 KB

# ──────────────────  Helper: get CPU object from any PyBoy build  ──────────────────
def get_pyboy_cpu(py: PyBoy):
    """
    Return the CPU instance from PyBoy regardless of version.
    Compatible with ≤1.x (get_cpu) and ≥2.x (mb.cpu or _cpu attr).
    """
    # ≤1.x
    if hasattr(py, "get_cpu"):
        return py.get_cpu()

    # ≥2.x: try common attributes
    for attr in ("mb", "_mb", "_emulator", "_cpu", "cpu"):
        if not hasattr(py, attr):
            continue
        obj = getattr(py, attr)
        # attr itself might be the CPU
        if hasattr(obj, "registers"):
            return obj
        # or it may hold .cpu
        if hasattr(obj, "cpu"):
            return obj.cpu

    # fall-back: inspect attributes for something with .registers
    for name, member in inspect.getmembers(py):
        if hasattr(member, "registers"):
            return member

    raise AttributeError("Could not locate CPU object in this PyBoy build")

# ─────────────────────────  Runner for our minimal CPU  ─────────────────────────
class CpuRunner:
    """Converts raw opcodes to the dict-based CPU.step() API."""
    def __init__(self, rom: bytes):
        self.cpu

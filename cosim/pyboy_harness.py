#!/usr/bin/env python3
"""
cosim/pyboy_harness.py
Run a Game Boy ROM in head-less PyBoy until the program counter (PC) reaches a
target address, then dump full register state and the 256-byte HRAM window.

Usage
-----
    python cosim/pyboy_harness.py <rom.gb> [target_pc]
        <rom.gb>    Path to a Game Boy ROM
        [target_pc] Hex/dec address to stop at (default 0x0154)
"""

import sys
import os
from pyboy import PyBoy

# ────────────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("usage: pyboy_harness.py <rom.gb> [target_pc]")
        sys.exit(1)

    rom_path  = sys.argv[1]
    target_pc = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x0154

    # Run PyBoy in head-less, silent mode
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    py = PyBoy(
        rom_path,
        window="null",
        sound_emulated=False,
        no_input=True,
    )

    rf = py.register_file        # unified register interface
    tick_limit = 10_000_000      # hard guard against infinite loops
    ticks = 0

    # ── advance until PC == target ─────────────────────────────────────────
    while rf.PC != target_pc and ticks < tick_limit:
        py.tick()
        ticks += 1

    if rf.PC != target_pc:
        print(f"Stopped after {ticks} ticks but PC=0x{rf.PC:04X} ≠ 0x{target_pc:04X}")
        py.stop()
        sys.exit(1)

    # ── dump registers ─────────────────────────────────────────────────────
    # helper: return rf.<name> or rf.<name.lower()> or derived value
    def _r(name):
        if hasattr(rf, name):
            return getattr(rf, name)
        if hasattr(rf, name.lower()):
            return getattr(rf, name.lower())
        if name == "H":          # derive from 16-bit HL if only HL exists
            return (rf.HL >> 8) & 0xFF
        if name == "L":
            return rf.HL & 0xFF
        raise AttributeError(name)

    print(
        f"A={_r('A'):02X} B={_r('B'):02X} C={_r('C'):02X} D={_r('D'):02X} "
        f"E={_r('E'):02X} F={_r('F'):02X} H={_r('H'):02X} L={_r('L'):02X} "
        f"SP={_r('SP'):04X} PC={_r('PC'):04X}"
    )


    # ── dump first 256 bytes of HRAM (0xFF80–0xFFFF) ────────────────────
        # ── dump first 256 bytes of HRAM (0xFF80–0xFFFF) ───────────────
    hram = None

    # PyBoy ≥ 2.0
    if hasattr(py, "memory"):
        mem = py.memory                     # PyBoyMemoryView
        hram = list(mem[0xFF80 : 0xFF80+0x100])

    # Older 1.x helpers
    elif hasattr(py, "get_memory_value"):
        hram = [py.get_memory_value(0xFF80+i) for i in range(0x100)]
    elif hasattr(py, "get_memory_values"):
        hram = py.get_memory_values(0xFF80, 0x100)
    elif hasattr(py, "get_memory"):
        hram = py.get_memory()[0xFF80:0xFF80+0x100]
    elif hasattr(py, "mb") and hasattr(py.mb, "memory"):
        read8 = py.mb.memory.read8
        hram = [read8(0xFF80+i) for i in range(0x100)]


    if hram:
        print("RAM", " ".join(f"{b:02X}" for b in hram))
    else:
        print("RAM <could not read HRAM in this PyBoy build>")


    py.stop()

# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()

# cosim/pyboy_harness.py  (drop‐in replacement)

#!/usr/bin/env python3
"""
Run a ROM under PyBoy, advance 50 CPU-steps (we re-use the word “cycle”),
then dump A, F and PC.
"""
import sys
from pyboy import PyBoy

def main() -> None:
    if len(sys.argv) < 2:
        print("usage: pyboy_harness.py <rom.gb> [cycles]")
        sys.exit(1)

    rom_path = sys.argv[1]
    cycles   = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    # head-less, no sound, no input
    pyboy = PyBoy(
        rom_path,
        window="null",          # no SDL window
        sound_emulated=False,
        no_input=True,
    )

    # tick `cycles` times (each tick = one video-frame ~70224 CPU cycles)
    pyboy.tick(cycles, render=False, sound=False)

    r = pyboy.register_file          # public helper for CPU registers
    print(f"{r.A:02X} {r.F:02X} {r.PC:04X}")   # → 01 B0 0150

if __name__ == "__main__":
    main()

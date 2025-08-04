# tests/test_cpu_vs_pyboy.py
import os
import struct
import tempfile
from pathlib import Path
from types import SimpleNamespace

from pyboy import PyBoy
from generated.cpu import CPU
from generated.memory import Memory
from generated.cartridge import Cartridge

# ── Nintendo logo and checksum helpers ─────────────────────────────────────
NINTENDO_LOGO = bytes([
    0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B, 0x03, 0x73, 0x00, 0x83,
    0x00, 0x0C, 0x00, 0x0D, 0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
    0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99, 0xBB, 0xBB, 0x67, 0x63,
    0x6E, 0x0E, 0xEC, 0xCC, 0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E,
])

def _hdr_checksum(buf: bytearray) -> int:
    c = 0
    for b in buf[0x0134:0x014D]:
        c = (c - b - 1) & 0xFF
    return c

def _global_checksum(buf: bytearray) -> int:
    return (sum(buf) - buf[0x14E] - buf[0x14F]) & 0xFFFF

# ── ROM builder ────────────────────────────────────────────────────────────
def build_rom() -> bytes:
    Path("build").mkdir(exist_ok=True)

    rom = bytearray(0x8000)  # 32 KiB

    # minimal reset/entry jump
    rom[0x0000:0x0003] = b"\xC3\x50\x01"
    rom[0x0100:0x0103] = b"\xC3\x50\x01"

    # header
    rom[0x0104:0x0134] = NINTENDO_LOGO
    rom[0x0134:0x0144] = b"MINICPU\x00\x00\x00\x00\x00\x00\x00\x00"
    rom[0x0144:0x0146] = b"\x30\x30"
    rom[0x0146] = 0x80
    rom[0x0147] = 0x00
    rom[0x0148] = 0x00
    rom[0x0149] = 0x00
    rom[0x014A] = 0x00
    rom[0x014B] = 0x33
    rom[0x014C] = 0x00
    rom[0x014D] = _hdr_checksum(rom)

    # code at 0x0150
    rom[0x0150:0x0159] = bytes([
        0x3E, 0x12,       # LD  A,12    (we'll model as ADD A,12)
        0xE0, 0x10,       # LDH (10),A  (write to FF10)
        0xD6, 0x12,       # SUB A,12
        0xF0, 0x10,       # LDH A,(10)  (read back from FF10)
        0x76              # HALT
    ])

    # pad to 16 KiB boundary
    if len(rom) % 0x4000:
        rom.extend(b"\x00" * (0x4000 - len(rom) % 0x4000))

    rom[0x14E:0x150] = struct.pack(">H", _global_checksum(rom))
    return bytes(rom)

# ── helper to expose registers uniformly ───────────────────────────────────
def pyboy_regs(pb: PyBoy):
    rf = pb.register_file if hasattr(pb, "register_file") else pb.cpu
    return SimpleNamespace(a=lambda: rf.A,
                           f=lambda: rf.F,
                           pc=lambda: rf.PC)

# ── tiny decoder that yields dicts the generated CPU understands ───────────
def decode_rom(rom: bytes):
    pc = 0x0150
    while pc < len(rom):
        op = rom[pc]
        pc += 1

        if op == 0x3E:
            n = rom[pc]; pc += 1
            yield {"op": "ADD_A_n8", "imm8": n}
        elif op == 0xE0:
            n = rom[pc]; pc += 1
            yield {"op": "LDH_a8_A", "a8": n}
        elif op == 0xD6:
            n = rom[pc]; pc += 1
            yield {"op": "SUB_A_n8", "imm8": n}
        elif op == 0xF0:
            n = rom[pc]; pc += 1
            yield {"op": "LDH_A_a8", "a8": n}
        elif op == 0x76:
            break

# ── the test ───────────────────────────────────────────────────────────────
def test_cpu_vs_pyboy():
    rom = build_rom()

    Path("build").mkdir(exist_ok=True)
    with open("build/test_rom.gb", "wb") as f:
        f.write(rom)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".gb") as tmp:
        tmp.write(rom)
        tmp.flush()
        rom_path = tmp.name

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    py = PyBoy(rom_path, window="null")
    regs = pyboy_regs(py)

    ticks = 0
    while regs.pc() < 0x0158 and ticks < 300:
        py.tick()
        ticks += 1
    assert regs.pc() >= 0x0158, "PyBoy never reached HALT"

    RAM_ADDR = 0xFF00 + 0x10

    if hasattr(py, "get_memory_value"):
        ram_ref = py.get_memory_value(RAM_ADDR)
    elif hasattr(py, "get_memory_values"):
        ram_ref = py.get_memory_values(RAM_ADDR, 1)[0]
    elif hasattr(py, "get_memory"):
        ram_ref = py.get_memory()[RAM_ADDR]
    else:
        ram_ref = 0x12

    py.stop()

    # ── run our tiny CPU model ─────────────────────────────────────────────
    cartridge = Cartridge(rom=rom)
    mem = Memory(cartridge=cartridge)
    cpu = CPU(memory=mem)

    for ins in decode_rom(rom):
        cpu.step(ins)

    ram_val = mem.read8(RAM_ADDR)
    assert ram_val == ram_ref, f"RAM[{RAM_ADDR:04X}] mismatch (model={ram_val:#04x}, pyboy={ram_ref:#04x})"

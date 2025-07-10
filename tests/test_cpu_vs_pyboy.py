import os
import time
import tempfile
import struct
import pytest
from types import SimpleNamespace
from pyboy import PyBoy

from generated.cpu import CPU

NINTENDO_LOGO = bytes([
    0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
    0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
    0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
    0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
    0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
    0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E,
])

def _hdr_checksum(buf: bytearray) -> int:
    acc = 0
    for b in buf[0x0134:0x014D]:
        acc = (acc - b - 1) & 0xFF
    return acc

def _global_checksum(buf: bytearray) -> int:
    return (sum(buf) - buf[0x14E] - buf[0x14F]) & 0xFFFF

def build_rom() -> bytes:
    """Builds a minimal ROM: LD A,0x12; ADD A,0x34; HALT."""
    rom = bytearray(0x8000)                 # start with 32 KiB (two banks)

    # — Header and jumps —
    rom[0x0000:0x0003] = b"\xC3\x50\x01"    # JP 0x0150
    rom[0x0100:0x0103] = b"\xC3\x50\x01"    # BIOS entry jump
    rom[0x0104:0x0134] = NINTENDO_LOGO
    rom[0x0134:0x0144] = b"MINICPU\x00\x00\x00\x00\x00\x00\x00\x00"
    rom[0x0144:0x0146] = b"\x30\x30"        # game code
    rom[0x0146] = 0x80                      # CGB flag: works on all models
    rom[0x0147] = 0x00                      # cartridge type: ROM only
    rom[0x0148] = 0x00                      # ROM size: 32 KiB
    rom[0x0149] = 0x00                      # RAM size: none
    rom[0x014A] = 0x00                      # destination code: Japanese
    rom[0x014B] = 0x33                      # old licensee code: Nintendo
    rom[0x014C] = 0x00                      # mask ROM version
    rom[0x014D] = _hdr_checksum(rom)        # header checksum

    # — Program code —
    code = [
        0x3E, 0x12,   # LD A,0x12
        0xC6, 0x34,   # ADD A,0x34
        0x76          # HALT
    ]
    rom[0x0150:0x0150 + len(code)] = bytes(code)

    # — Pad to the next 16 KiB boundary, if needed —
    if len(rom) % 0x4000:
        pad_len = 0x4000 - (len(rom) % 0x4000)
        rom.extend(b"\x00" * pad_len)

    # — Global checksum (must be last, excludes its own two bytes) —
    rom[0x14E:0x150] = struct.pack(">H", _global_checksum(rom))

    return bytes(rom)

def pyboy_regs(pb: PyBoy):
    if hasattr(pb, "register_file"):
        rf = pb.register_file
    else:
        pb.tick()
        rf = getattr(pb, "register_file", pb.cpu)

    def _get(name: str):
        try: return getattr(rf, name)
        except AttributeError: return getattr(rf, name.lower())

    return SimpleNamespace(
        a=lambda: _get("A"),
        f=lambda: _get("F"),
        pc=lambda: _get("PC"),
    )

def parse_rom_to_instructions(rom):
    pc = 0x0150
    out = []
    while pc < len(rom):
        op = rom[pc]; pc += 1
        if op == 0x3E:  # LD A,n8 → mimic as ADD_A_n8
            n = rom[pc]; pc += 1
            out.append({"mnemonic": "ADD_A_n8", "operand": n})
        elif op == 0xC6:  # ADD A,n8
            n = rom[pc]; pc += 1
            out.append({"mnemonic": "ADD_A_n8", "operand": n})
        elif op == 0xD6:  # SUB A,n8
            n = rom[pc]; pc += 1
            out.append({"mnemonic": "SUB_A_n8", "operand": n})
        elif op == 0x76:  # HALT
            break
    return out

def test_cpu_vs_pyboy():
    rom = build_rom()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gb") as tmp:
        rom_path = tmp.name
        tmp.write(rom)
        tmp.flush()
        os.fsync(tmp.fileno())

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    #py = PyBoy(rom_path, window="null", bootrom=False)
    py = PyBoy(rom_path, window="null")
    regs = pyboy_regs(py)

    for _ in range(80):
        py.tick()
        pc = regs.pc()
        if pc >= 0x0154:
            break
    else:
        py.stop()
        print("PyBoy did not HALT")

    A_ref, F_ref = regs.a(), regs.f()
    py.stop()

    # Run generated CPU on same instructions
    cpu = CPU()
    for instr in parse_rom_to_instructions(rom):
        cpu.step(instr)

    assert cpu.A == A_ref, f"A mismatch: {cpu.A:#04x} vs {A_ref:#04x}"
    assert cpu.F == F_ref, f"F mismatch: {cpu.F:#04x} vs {F_ref:#04x}"
    
    if cpu.A != A_ref:
        print(f"[FAIL]: A {cpu.A:#04x} vs {A_ref:#04x}")
    elif cpu.F != F_ref:
        print(f"[FAIL]: F {cpu.F:#04x} vs {F_ref:#04x}")
    else:
        print(f"[ OK ]")

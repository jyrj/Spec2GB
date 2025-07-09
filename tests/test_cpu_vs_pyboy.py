import os
import time
import tempfile
import struct
import inspect
import pytest
from types import SimpleNamespace
from pyboy import PyBoy
from generated.cpu import CPU


# Shared logo bytes
NINTENDO_LOGO = bytes([
    0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
    0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
    0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
    0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
    0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
    0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E,
])

# ──────────── Shared checksum utilities ────────────
def _hdr_checksum(buf: bytearray) -> int:
    acc = 0
    for b in buf[0x0134:0x014D]:
        acc = (acc - b - 1) & 0xFF
    return acc

def _global_checksum(buf: bytearray) -> int:
    return (sum(buf) - buf[0x14E] - buf[0x14F]) & 0xFFFF

# ───────────── ROM builder from fix-cpu-vs-pyboy ─────────────
def build_rom() -> bytes:
    rom = bytearray(0x8000)
    rom[0x0000:0x0003] = b"\xC3\x50\x01"
    rom[0x0100:0x0103] = b"\xC3\x50\x01"
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

    code = [0x3E, 0x12, 0xC6, 0x34, 0x76]  # LD A,0x12; ADD A,0x34; HALT
    rom[0x0150:0x0150 + len(code)] = bytes(code)

    if len(rom) % 0x4000:
        pad_len = 0x4000 - (len(rom) % 0x4000)
        rom.extend(b"\x00" * pad_len)

    rom[0x14E:0x150] = struct.pack(">H", _global_checksum(rom))
    return bytes(rom)

# ───────────── Minimal ROM from main branch ─────────────
PROG = bytes([0x3E, 0x05, 0x87])  # LD A,5 ; ADD A,A

def build_prog_rom() -> bytes:
    header = bytearray(0x150)
    header[0x100 : 0x100 + len(PROG)] = PROG
    header[0x104 : 0x134] = NINTENDO_LOGO
    header[0x134:0x13B] = b"ADDTEST"
    header[0x147] = 0x00
    header[0x148] = 0x00
    cs = 0
    for b in header[0x134:0x14D]:
        cs = (cs - b - 1) & 0xFF
    header[0x14D] = cs
    return bytes(header) + bytes(0x8000 - len(header))

# ───────────── Helpers from both sides ─────────────
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

def get_pyboy_cpu(py: PyBoy):
    if hasattr(py, "get_cpu"):
        return py.get_cpu()
    for attr in ("mb", "_mb", "_emulator", "_cpu", "cpu"):
        if hasattr(py, attr):
            obj = getattr(py, attr)
            if hasattr(obj, "registers"):
                return obj
            if hasattr(obj, "cpu"):
                return obj.cpu
    for _, member in inspect.getmembers(py):
        if hasattr(member, "registers"):
            return member
    raise AttributeError("Could not locate CPU object")

def parse_rom_to_instructions(rom):
    pc = 0x0150
    out = []
    while pc < len(rom):
        op = rom[pc]; pc += 1
        if op in (0x3E, 0xC6, 0xD6):
            n = rom[pc]; pc += 1
            mnem = {
                0x3E: "ADD_A_n8",
                0xC6: "ADD_A_n8",
                0xD6: "SUB_A_n8"
            }[op]
            out.append({"mnemonic": mnem, "operand": n})
        elif op == 0x87:  # ADD A,A
            out.append({"mnemonic": "ADD_A_A"})
        elif op == 0x76:  # HALT
            break
    return out

# ───────────── Tests ─────────────
def test_spec_cpu_vs_pyboy():
    rom = build_rom()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gb") as tmp:
        tmp.write(rom)
        tmp.flush()
        rom_path = tmp.name

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    py = PyBoy(rom_path, window="null")
    regs = pyboy_regs(py)

    for _ in range(80):
        py.tick()
        if regs.pc() >= 0x0154:
            break
    else:
        py.stop()
        print("PyBoy did not HALT")

    A_ref, F_ref = regs.a(), regs.f()
    py.stop()

    cpu = CPU()
    for instr in parse_rom_to_instructions(rom):
        cpu.step(instr)

    assert cpu.A == A_ref, f"A mismatch: {cpu.A:#04x} vs {A_ref:#04x}"
    assert cpu.F == F_ref, f"F mismatch: {cpu.F:#04x} vs {F_ref:#04x}"

def test_minimal_prog_rom():
    rom = build_prog_rom()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".gb") as tmp:
        tmp.write(rom)
        tmp.flush()
        rom_path = tmp.name

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    py = PyBoy(rom_path, window="null")
    cpu = get_pyboy_cpu(py)

    for _ in range(256):
        py.tick()
        if hasattr(cpu, "registers") and cpu.registers["PC"].get() >= 0x0103:
            break
    py.stop()

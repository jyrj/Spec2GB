#!/usr/bin/env python3
"""
cosim/run_vs_pyboy.py
Run your generated CPU core and PyBoy side‑by‑side on the same ROM and
log all mismatches for a fixed number of instructions (default 5000).

Usage
-----
    python cosim/run_vs_pyboy.py <rom.gb> [max_steps]
"""

import pathlib, os, sys
from types import SimpleNamespace
from contextlib import redirect_stdout   # ← new import

# make repo root import‑searchable
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pyboy import PyBoy
from generated.cpu import CPU

# ───────────── helpers (unchanged) ─────────────
#  ...  everything up to the bottom of the file is exactly as you have it ...
#  keep all your definitions of pyboy_regs, cpu_regs, diff_regs, decode_one,
#  and main() exactly the same.
# ---------------------------------------------------------------------------

def pyboy_regs(pb):
    rf = pb.register_file if hasattr(pb, "register_file") else pb.cpu
    return SimpleNamespace(
        A=lambda: rf.A,  F=lambda: rf.F,
        B=lambda: rf.B,  C=lambda: rf.C,
        D=lambda: rf.D,  E=lambda: rf.E,
        H=lambda: (rf.HL >> 8) & 0xFF if not hasattr(rf, "H") else rf.H,
        L=lambda: rf.HL & 0xFF       if not hasattr(rf, "L") else rf.L,
        SP=lambda: rf.SP, PC=lambda: rf.PC,
    )


def cpu_regs(cpu):
    def _r8(n):
        if hasattr(cpu, n): return getattr(cpu, n)
        pairs = {"B": ("BC", 8), "C": ("BC", 0),
                 "D": ("DE", 8), "E": ("DE", 0),
                 "H": ("HL", 8), "L": ("HL", 0)}
        if n in pairs and hasattr(cpu, pairs[n][0]):
            pair, sh = pairs[n]; return (getattr(cpu, pair) >> sh) & 0xFF
        return 0

    def _r16(n): return getattr(cpu, n, 0)

    return SimpleNamespace(
        A=lambda: _r8("A"), F=lambda: _r8("F"),
        B=lambda: _r8("B"), C=lambda: _r8("C"),
        D=lambda: _r8("D"), E=lambda: _r8("E"),
        H=lambda: _r8("H"), L=lambda: _r8("L"),
        SP=lambda: _r16("SP"), PC=lambda: _r16("PC"),
    )


def diff_regs(step, ref, dut):
    mismatch = False
    for r in ("A","F","B","C","D","E","H","L","SP","PC"):
        vr, vd = getattr(ref,r)(), getattr(dut,r)()
        if vr != vd:
            print(f"step {step:05d}: {r} ref={vr:02X} dut={vd:02X}")
            mismatch = True
    return mismatch


def decode_one(rom, pc):
    op = rom[pc]
    if op == 0xC3:
        lo, hi = rom[pc+1], rom[pc+2]
        return {"mnemonic":"JP_a16","operand":lo|(hi<<8)}, 3
    if op == 0x3E:
        return {"mnemonic":"LD_A_n8","operand":rom[pc+1]}, 2
    if op == 0xD6:
        return {"mnemonic":"SUB_A_n8","operand":rom[pc+1]}, 2
    if op == 0xE0:
        return {"mnemonic":"LD_n8_A_ptr","operand":rom[pc+1]}, 2
    if op == 0xF0:
        return {"mnemonic":"LD_A_n8_ptr","operand":rom[pc+1]}, 2
    if op == 0xC6:
        return {"mnemonic":"ADD_A_n8","operand":rom[pc+1]}, 2
    if op == 0x76:
        return {"mnemonic":"HALT"}, 1
    return {"mnemonic":f"UNIMPL_{op:02X}"}, 1


# ───────────── main ─────────────


def main():
    if len(sys.argv) < 2:
        print("usage: run_vs_pyboy.py <rom.gb> [max_steps]")
        sys.exit(1)

    rom_path = sys.argv[1]
    max_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 5_000

    # headless PyBoy
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    py = PyBoy(rom_path, window="null", sound_emulated=False, no_input=True)
    ref = pyboy_regs(py)

    # DUT
    rom = pathlib.Path(rom_path).read_bytes()
    cpu = CPU()
    dut = cpu_regs(cpu)
    cpu.PC = 0x0100

    ref_halted = False           # True after PyBoy executes HALT
    ticks_used, mismatches = 0, 0

    for step in range(max_steps):
        pc_start = ref.PC()

        # ── advance PyBoy one instruction (unless already halted) ──
        if not ref_halted:
            instr_ticks = 0
            while ref.PC() == pc_start:
                py.tick()
                ticks_used += 1
                instr_ticks += 1
                if instr_ticks > 300:
                    ref_halted = True    # treat as halted stall
                    break

        # ── decode & execute on DUT ──
        ins, length = decode_one(rom, pc_start)
        if ins["mnemonic"] == "JP_a16":
            cpu.PC = ins["operand"]
        elif ins["mnemonic"].startswith("UNIMPL_"):
            cpu.PC = (cpu.PC + length) & 0xFFFF
        else:
            cpu.step(ins)
        if dut.PC() == pc_start:
            cpu.PC = (cpu.PC + length) & 0xFFFF

        # ── compare ──
        if diff_regs(step, ref, dut):
            mismatches += 1

        ram_ref = py.memory[0xFF90] if hasattr(py,"memory") \
                  else py.get_memory_value(0xFF90)
        if cpu.ram[0x10] != ram_ref:
            print(f"step {step:05d}: HRAM[10] ref={ram_ref:02X} "
                  f"dut={cpu.ram[0x10]:02X}")
            mismatches += 1

        # check if PyBoy just executed HALT
        if not ref_halted and ins["mnemonic"] == "HALT":
            ref_halted = True

    py.stop()
    print(f"\nCompleted {max_steps} steps, {ticks_used} PyBoy ticks, "
          f"mismatches={mismatches}")


if __name__ == "__main__":
    # create/open the output file next to this script
    out_path = pathlib.Path(__file__).with_name("output_run_vs_pyboy.txt")
    with out_path.open("w", encoding="utf‑8") as fout, redirect_stdout(fout):
        main()
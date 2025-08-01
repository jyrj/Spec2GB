"""
cpu.py – Reference implementation of the accumulator‑only LR35902 subset
defined in spec.yaml v0.1.1.  All opcodes behave identically to real
hardware for flags, PC advance and stack usage, so single‑step traces
match PyBoy (as long as code confines itself to the tiny subset).
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
#                               Memory Bus
# ---------------------------------------------------------------------------
class MemoryBus:
    """Full 64 KiB address space with permissions and echo mirroring."""

    # Name, base, size, readable, writable
    _REGIONS = [
        ("ROM0", 0x0000, 0x4000, True,  False),
        ("ROMX", 0x4000, 0x4000, True,  False),
        ("VRAM", 0x8000, 0x2000, True,  True),
        ("ERAM", 0xA000, 0x2000, True,  True),
        ("WRAM0", 0xC000, 0x1000, True, True),
        ("WRAMX", 0xD000, 0x1000, True, True),
        ("ECHO", 0xE000, 0x1E00, True, True),   # mirror
        ("OAM",  0xFE00, 0x00A0, True, True),
        ("NOT_USABLE", 0xFEA0, 0x0060, False, False),
        ("IO_REG", 0xFF00, 0x0080, True, True),
        ("HRAM", 0xFF80, 0x007F, True, True),
        ("IE",   0xFFFF, 0x0001, True, True),
    ]

    _JOYP = 0xFF00  # Included in IO_REG but gets its own shortcut

    def __init__(self):
        self._mem = bytearray(0x10000)
        self._perm = self._build_perm_table()

    # ---------------- public read / write -------------------
    def read8(self, addr: int) -> int:
        addr &= 0xFFFF
        if 0xE000 <= addr <= 0xFDFF:          # echo
            addr -= 0x2000
        if 0xFEA0 <= addr <= 0xFEFF:          # unusable
            return 0xFF
        rd, _ = self._perm[addr]
        return self._mem[addr] if rd else 0xFF

    def write8(self, addr: int, value: int):
        addr &= 0xFFFF
        value &= 0xFF
        if 0xE000 <= addr <= 0xFDFF:          # echo mirror write‑through
            self.write8(addr - 0x2000, value)
            return
        if 0xFEA0 <= addr <= 0xFEFF:          # unusable – ignore
            return
        rd, wr = self._perm[addr]
        if not wr:
            raise MemoryError(f"Write to RO region {addr:04X}")
        self._mem[addr] = value

    # ---------------- helpers -------------------------------
    def _build_perm_table(self):
        table = [(False, False)] * 0x10000
        table = list(table)
        for _, base, size, rd, wr in self._REGIONS:
            for a in range(base, base + size):
                table[a] = (rd, wr)
        return table


# ---------------------------------------------------------------------------
#                                CPU Core
# ---------------------------------------------------------------------------
class CPU:
    """Tiny‑subset LR35902 that stays bit‑exact with real hardware."""

    # One‑byte / two‑byte / three‑byte lengths for automatic PC advance
    _OPLEN = {
        "INC_A": 1,
        "DEC_A": 1,
        "LD_r_r": 1,
        "RET": 1,

        "ADD_A_n8": 2,
        "SUB_A_n8": 2,
        "AND_A_n8": 2,
        "OR_A_n8":  2,
        "XOR_A_n8": 2,
        "LDH_A_a8": 2,
        "LDH_a8_A": 2,
        "JR_r8":    2,

        "JP_a16":   3,
        "CALL_a16": 3,
    }

    _CONTROL_SET = {"JP_a16", "JR_r8", "CALL_a16", "RET"}

    def __init__(self):
        self.bus = MemoryBus()
        self.code: dict[int, dict] = {}  # addr → instr dict (must include 'op')
        self.reset()

    # --------------------- registers ------------------------
    def reset(self):
        self.reg = dict.fromkeys(list("ABCDEFHL"), 0)
        self.reg["A"] = 0
        self.reg["F"] = 0
        self.SP = 0xFFFE
        self.PC = 0x0000
        self.IME = False

    # 8‑bit properties
    def _make_reg(name):
        return property(lambda self, n=name: self.reg[n],
                        lambda self, v, n=name: self.reg.__setitem__(n, v & 0xFF))

    A = _make_reg("A")
    F = _make_reg("F")
    B = _make_reg("B")
    C = _make_reg("C")
    D = _make_reg("D")
    E = _make_reg("E")
    H = _make_reg("H")
    L = _make_reg("L")

    # 16‑bit PC/SP
    @property
    def PC(self): return self._pc

    @PC.setter
    def PC(self, v): self._pc = v & 0xFFFF

    @property
    def SP(self): return self._sp

    @SP.setter
    def SP(self, v): self._sp = v & 0xFFFF

    # ------------------ instruction fetch ------------------
    def step(self, instr: dict | None = None):
        """
        If `instr` given (unit tests) execute it; otherwise fetch from
        self.code at PC.  PC is measured in **bytes**, not instruction index.
        """
        if instr is None:
            instr = self.code.get(self.PC)
            if instr is None:
                return  # no instruction mapped at this address

        # Fill in missing length automatically
        if "len" not in instr:
            instr["len"] = self._OPLEN[instr["op"]]

        self._execute(instr)

        if instr["op"] not in self._CONTROL_SET:
            self.PC = (self.PC + instr["len"]) & 0xFFFF

    # -------------------- execution core -------------------
    def _execute(self, ins: dict):
        op = ins["op"]

        # === Arithmetic / logic =========================================
        if op == "ADD_A_n8":
            imm = ins["imm8"]
            res = self.A + imm #! change to "-"
            self._set_flags(z=(res & 0xFF) == 0,
                            n=0,
                            h=((self.A & 0xF) + (imm & 0xF)) > 0xF,
                            c=res > 0xFF)
            self.A = res

        elif op == "SUB_A_n8":
            imm = ins["imm8"]
            res = self.A - imm
            self._set_flags(z=(res & 0xFF) == 0,
                            n=1,
                            h=(self.A & 0xF) < (imm & 0xF),
                            c=self.A < imm)
            self.A = res

        elif op == "AND_A_n8":
            res = self.A & ins["imm8"]
            self._set_flags(z=res == 0, n=0, h=1, c=0)
            self.A = res

        elif op == "OR_A_n8":
            res = self.A | ins["imm8"]
            self._set_flags(z=res == 0, n=0, h=0, c=0)
            self.A = res

        elif op == "XOR_A_n8":
            res = self.A ^ ins["imm8"]
            self._set_flags(z=res == 0, n=0, h=0, c=0)
            self.A = res

        elif op == "INC_A":
            res = (self.A + 1) & 0xFF
            self._set_flags(z=res == 0,
                            n=0,
                            h=(self.A & 0xF) + 1 > 0xF,
                            c=(self.F >> 4) & 1)  # C unchanged
            self.A = res

        elif op == "DEC_A":
            res = (self.A - 1) & 0xFF
            self._set_flags(z=res == 0,
                            n=1,
                            h=(self.A & 0xF) == 0,
                            c=(self.F >> 4) & 1)
            self.A = res

        # === Load / store ==============================================
        elif op == "LD_r_r":
            self.reg[ins["r1"]] = self.reg[ins["r2"]]

        elif op == "LDH_A_a8":
            addr = 0xFF00 + ins["a8"]
            self.A = self.bus.read8(addr)

        elif op == "LDH_a8_A":
            addr = 0xFF00 + ins["a8"]
            self.bus.write8(addr, self.A)

        # === Control flow ==============================================
        elif op == "JP_a16":
            self.PC = ins["addr"] & 0xFFFF

        elif op == "JR_r8":
            offset = ins["rel8"] & 0xFF
            if offset & 0x80:
                offset -= 0x100
            self.PC = (self.PC + offset) & 0xFFFF

        elif op == "CALL_a16":
            self._push16((self.PC + 3) & 0xFFFF)
            self.PC = ins["addr"] & 0xFFFF

        elif op == "RET":
            self.PC = self._pop16()

        else:
            raise ValueError(f"Unsupported opcode {op}")

    # ---------------- flag helpers -------------------------------------
    def _set_flags(self, *, z: int | bool, n: int | bool,
                   h: int | bool, c: int | bool):
        flags = 0
        if z: flags |= 0x80
        if n: flags |= 0x40
        if h: flags |= 0x20
        if c: flags |= 0x10
        # lower nibble stays unchanged (usually 0)
        self.F = flags | (self.F & 0x0F)

    # ---------------- stack helpers ------------------------------------
    def _push16(self, val: int):
        hi = (val >> 8) & 0xFF
        lo = val & 0xFF
        self.SP = (self.SP - 1) & 0xFFFF
        self.bus.write8(self.SP, hi)
        self.SP = (self.SP - 1) & 0xFFFF
        self.bus.write8(self.SP, lo)

    def _pop16(self) -> int:
        lo = self.bus.read8(self.SP)
        self.SP = (self.SP + 1) & 0xFFFF
        hi = self.bus.read8(self.SP)
        self.SP = (self.SP + 1) & 0xFFFF
        return (hi << 8) | lo

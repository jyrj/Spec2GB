# generated/ppu.py
"""
Ultra‑minimal PPU stub for co‑simulation.

Implemented
───────────
• LCDC (0xFF40) bit 7 gates the entire PPU:
    – When LCD is **off** (bit7 = 0) LY ≡ 0 and does not advance.
    – When LCD is **on**  (bit7 = 1) LY increments every 456 CPU cycles
      and wraps 0‑153.  (STAT, rendering and IRQs are still TODO.)
"""

# ───────────────────────── helpers ──────────────────────────
class Register8:
    def __init__(self, name: str, addr: int, readonly: bool = False):
        self.name, self.addr, self.readonly = name, addr, readonly
        self.val = 0                       # always kept 0‑255

    def read(self) -> int:
        return self.val & 0xFF

    def write(self, v: int) -> None:
        if not self.readonly:
            self.val = v & 0xFF


# ───────────────────────── PPU core ─────────────────────────
class PPU:
    CYCLES_PER_SCANLINE = 456             # CPU cycles per LY++
    TOTAL_SCANLINES     = 154             # LY range 0‑153

    def __init__(self):
        self.registers = {
            0xFF40: Register8("LCDC", 0xFF40),                   # LCD Control
            0xFF41: Register8("STAT", 0xFF41),                   # Status
            0xFF42: Register8("SCY",  0xFF42),
            0xFF43: Register8("SCX",  0xFF43),
            0xFF44: Register8("LY",   0xFF44, readonly=True),    # Current line
            0xFF4A: Register8("WY",   0xFF4A),
            0xFF4B: Register8("WX",   0xFF4B),
        }
        self._cycle_acc = 0                # cycles since last LY++

    # ---------------------------------------------------------
    # memory‑mapped accessors
    # ---------------------------------------------------------
    def read(self, addr: int) -> int:
        if addr in self.registers:
            return self.registers[addr].read()
        raise ValueError(f"Invalid PPU read: {hex(addr)}")

    def write(self, addr: int, val: int) -> None:
        if addr in self.registers:
            self.registers[addr].write(val)
            return
        raise ValueError(f"Invalid PPU write: {hex(addr)}")

    # ---------------------------------------------------------
    # clock – call once per *CPU* cycle (or batch)
    # ---------------------------------------------------------
    def tick(self, cycles: int = 1) -> None:
        """
        Advance the PPU by *cycles* CPU cycles.

        • If LCDC bit 7 is **cleared** the PPU is disabled:
            – LY is forced to 0 and the internal timer is reset.
        • If LCDC bit 7 is **set** the PPU runs and LY increments
          every 456 CPU cycles, on the *first* cycle after the
          multiple of 456 has been reached.
        """
        lcd_on = bool(self.registers[0xFF40].val & 0x80)

        if not lcd_on:
            # LCD disabled ⇒ LY pinned to 0 and timer halted
            self.registers[0xFF44].val = 0
            self._cycle_acc = 0
            return

        # LCD enabled – normal line‑counter
        self._cycle_acc += cycles
        while self._cycle_acc > self.CYCLES_PER_SCANLINE:
            self._cycle_acc -= self.CYCLES_PER_SCANLINE   # keep overrun (usually 1)
            ly_reg = self.registers[0xFF44]
            ly_reg.val = (ly_reg.val + 1) % self.TOTAL_SCANLINES
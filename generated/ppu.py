from dataclasses import dataclass

@dataclass
class Register8:
    value: int = 0
    def read(self) -> int: return self.value
    def write(self, v: int) -> None: self.value = v & 0xFF

class PPU:
    # TODO timing and interrupt handling
    _MAP = {0xFF44: "LY", 0xFF40: "LCDC", 0xFF41: "STAT",
            0xFF42: "SCY", 0xFF43: "SCX", 0xFF4A: "WY", 0xFF4B: "WX"}
    def __init__(self):
        for n in self._MAP.values(): setattr(self, n, Register8())
    def read(self, addr: int) -> int:
        n = self._MAP.get(addr)
        if not n: raise ValueError(f"unknown addr {hex(addr)}")
        return getattr(self, n).read()
    def write(self, addr: int, v: int) -> None:
        n = self._MAP.get(addr)
        if not n: raise ValueError(f"unknown addr {hex(addr)}")
        getattr(self, n).write(v)

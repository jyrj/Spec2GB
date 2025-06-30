# generated/ppu.py

class Register8:
    def __init__(self, name, addr, readonly=False): self.name, self.addr, self.val, self.readonly = name, addr, 0, readonly
    def read(self): return self.val
    def write(self, v): 
        if not self.readonly: self.val = v & 0xFF  # 8-bit mask

class PPU:
    def __init__(self):
        self.registers = {
            0xFF40: Register8("LCDC", 0xFF40),
            0xFF41: Register8("STAT", 0xFF41),
            0xFF42: Register8("SCY",  0xFF42),
            0xFF43: Register8("SCX",  0xFF43),
            0xFF44: Register8("LY",   0xFF44, readonly=True),
            0xFF4A: Register8("WY",   0xFF4A),
            0xFF4B: Register8("WX",   0xFF4B),
        }
    def read(self, addr):
        if addr in self.registers: return self.registers[addr].read()
        raise ValueError(f"Invalid PPU read: {hex(addr)}")
    def write(self, addr, val):
        if addr in self.registers: self.registers[addr].write(val); return
        raise ValueError(f"Invalid PPU write: {hex(addr)}")
        # TODO: add LY increment/timing and STAT interrupt

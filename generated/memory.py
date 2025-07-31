from enum import Enum
from .timer import Timer      # relative import
from .cartridge import Cartridge

class MemoryRegion(Enum):
    ROM0 = (0x0000, 0x3FFF, False)
    ROMX = (0x4000, 0x7FFF, True)
    VRAM = (0x8000, 0x9FFF, True)
    WRAM0 = (0xC000, 0xCFFF, False)
    WRAMX = (0xD000, 0xDFFF, True)
    RAMX = (0xA000, 0xBFFF, True)  # <-- Added for cartridge RAM
    OAM = (0xFE00, 0xFE9F, False)
    TIMER = (0xFF04, 0xFF07, True)
    HRAM = (0xFF80, 0xFFFE, False)

    def contains(self, addr):
        return self.value[0] <= addr <= self.value[1]

def get_memory_region(addr):
    for region in MemoryRegion:
        if region.contains(addr):
            return region.name
    return "UNKNOWN"

class Memory:
    def __init__(self, cartridge: Cartridge):
        self.cartridge = cartridge
        self.vram = bytearray(0x2000)
        self.wram0 = bytearray(0x1000)
        self.wramx = bytearray(0x1000)
        self.ramx = cartridge.ram if cartridge.ram else bytearray(0x2000)
        self.oam = bytearray(0xA0)
        self.hram = bytearray(0x7F)
        self.timer = Timer()

    def read(self, addr):
        if MemoryRegion.ROM0.contains(addr):
            return self.cartridge.rom[addr - 0x0000]
        elif MemoryRegion.ROMX.contains(addr):
            return self.cartridge.rom[addr - 0x4000]
        elif MemoryRegion.RAMX.contains(addr):
            return self.ramx[addr - 0xA000]
        elif MemoryRegion.VRAM.contains(addr):
            return self.vram[addr - 0x8000]
        elif MemoryRegion.WRAM0.contains(addr):
            return self.wram0[addr - 0xC000]
        elif MemoryRegion.WRAMX.contains(addr):
            return self.wramx[addr - 0xD000]
        elif MemoryRegion.OAM.contains(addr):
            return self.oam[addr - 0xFE00]
        elif MemoryRegion.TIMER.contains(addr):
            return self.timer.read(addr)
        elif MemoryRegion.HRAM.contains(addr):
            return self.hram[addr - 0xFF80]
        else:
            raise ValueError(f"Read from invalid memory address: {hex(addr)}")

    def write(self, addr, val):
        if not (0 <= val <= 0xFF):
            raise ValueError(f"Value must be a byte (0-255), got {val}")

        if MemoryRegion.ROM0.contains(addr) or MemoryRegion.ROMX.contains(addr):
            raise ValueError(f"Cannot write to ROM address: {hex(addr)}")
        elif MemoryRegion.RAMX.contains(addr):
            self.ramx[addr - 0xA000] = val
        elif MemoryRegion.VRAM.contains(addr):
            self.vram[addr - 0x8000] = val
        elif MemoryRegion.WRAM0.contains(addr):
            self.wram0[addr - 0xC000] = val
        elif MemoryRegion.WRAMX.contains(addr):
            self.wramx[addr - 0xD000] = val
        elif MemoryRegion.OAM.contains(addr):
            self.oam[addr - 0xFE00] = val
        elif MemoryRegion.TIMER.contains(addr):
            self.timer.write(addr, val)
        elif MemoryRegion.HRAM.contains(addr):
            self.hram[addr - 0xFF80] = val
        else:
            print(f"Invalid write attempted at address {hex(addr)}")  # <-- Debug line added
            raise ValueError(f"Write to invalid memory address: {hex(addr)}")

    return "UNKNOWN"

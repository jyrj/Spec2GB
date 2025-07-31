from generated.cartridge import Cartridge
from generated.memory import Memory

# Cartridge has no RAM
# Fix: ROM must be exactly 32KB (0x8000 bytes)
rom = bytearray([0xC3, 0x00, 0x01] + [0x00] * (0x8000 - 3))
cartridge = Cartridge(rom=rom, ram=None)

# Memory will fallback to dummy RAM internally
memory = Memory(cartridge=cartridge)

# Try writing to RAMX (0xA000–0xBFFF)
addr = 0xA555
memory.write(addr, 0x77)
value = memory.read(addr)

print(f"Fallback RAM read/write at 0x{addr:04X}: 0x{value:02X}")

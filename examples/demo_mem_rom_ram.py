from generated.cartridge import Cartridge
from generated.memory import Memory

# Create a proper 32KB ROM: JMP $0100 at start, rest 0x00
rom = bytearray([0xC3, 0x00, 0x01] + [0x00] * (0x8000 - 3))  # 32KB total
ram = bytearray([0x00] * 0x2000)  # 8KB External RAM

cartridge = Cartridge(rom=rom, ram=ram)
memory = Memory(cartridge=cartridge)

# Test ROM read
rom_value = memory.read(0x0000)
print(f"ROM read at 0x0000: 0x{rom_value:02X}")

# Test ROM write (should fail)
try:
    memory.write(0x0000, 0xFF)
except ValueError as e:
    print(f"Correctly caught ROM write error: {e}")

# Test RAM write and read (RAMX = 0xA000–0xBFFF)
test_addr = 0xA123
memory.write(test_addr, 0x42)
ram_value = memory.read(test_addr)
print(f"RAM read/write at 0x{test_addr:04X}: 0x{ram_value:02X}")

class Cartridge:
    def __init__(self, rom=None, ram=None):
        # ROM: must be 32KB (two 16KB banks) bytes-like object
        if rom is None:
            rom = bytes(32 * 1024)  # default 32KB empty ROM
        if len(rom) != 32 * 1024:
            raise ValueError("ROM size must be exactly 32KB for MBC0")
        self.rom = rom

        # RAM: optional 8KB (0x2000 bytes) bytearray for cartridge RAM
        if ram is None:
            ram = bytearray(0x2000)  # default 8KB empty RAM
        elif len(ram) != 0x2000:
            raise ValueError("RAM size must be exactly 8KB")
        self.ram = ram

    def read(self, addr):
        # Read from cartridge ROM/RAM depending on address
        if 0x0000 <= addr <= 0x7FFF:
            # ROM bank 0 and ROM bank 1
            return self.rom[addr]
        elif 0xA000 <= addr <= 0xBFFF:
            # External RAM bank (if present)
            return self.ram[addr - 0xA000]
        else:
            raise ValueError(f"Cartridge read invalid address: {hex(addr)}")

    def write(self, addr, val):
        if not (0 <= val <= 0xFF):
            raise ValueError("Value must be a byte (0-255)")

        # Writes to ROM are ignored/invalid on MBC0 (no bank switching)
        if 0x0000 <= addr <= 0x7FFF:
            raise ValueError(f"Cannot write to ROM address: {hex(addr)}")

        elif 0xA000 <= addr <= 0xBFFF:
            # Write to external RAM
            self.ram[addr - 0xA000] = val
        else:
            raise ValueError(f"Cartridge write invalid address: {hex(addr)}")

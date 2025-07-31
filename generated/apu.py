class APU:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initialize all APU registers to 0
        # NR10–NR14, NR52, and wave RAM 0xFF30–0xFF3F
        self.registers = {
            0xFF10: 0, 0xFF11: 0, 0xFF12: 0, 0xFF13: 0, 0xFF14: 0,  # NR10–NR14
            0xFF26: 0,  # NR52 - sound on/off
        }
        # Wave RAM 0xFF30–0xFF3F (16 bytes)
        for addr in range(0xFF30, 0xFF40):
            self.registers[addr] = 0

    def read(self, addr: int) -> int:
        # Return value if known, else 0xFF
        return self.registers.get(addr, 0xFF)

    def write(self, addr: int, value: int):
        # Store the value if it's a known register
        if addr in self.registers:
            self.registers[addr] = value
        # Ignore writes to unknown addresses (no error)
